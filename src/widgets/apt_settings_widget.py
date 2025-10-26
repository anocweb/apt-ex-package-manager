from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

class APTSettingsWidget(QWidget):
    """Settings widget for APT backend showing package sources"""
    
    def __init__(self, parent=None, logging_service=None):
        super().__init__(parent)
        self.logger = logging_service.get_logger('apt_settings') if logging_service else None
        self.setup_ui()
        self.load_sources()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("APT Package Sources")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Package sources from /etc/apt/sources.list and /etc/apt/sources.list.d/")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Sources table
        self.sources_table = QTableWidget()
        self.sources_table.setColumnCount(4)
        self.sources_table.setHorizontalHeaderLabels(["", "URI", "Suite", "Components"])
        self.sources_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.sources_table.setColumnWidth(0, 30)
        self.sources_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.sources_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.sources_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.sources_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sources_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sources_table.setWordWrap(True)
        self.sources_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.sources_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_sources)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def load_sources(self):
        """Load APT sources from system files"""
        sources = self._parse_sources()
        self.sources_table.setRowCount(len(sources))
        
        for row, source in enumerate(sources):
            # Enabled column
            enabled_item = QTableWidgetItem("✓" if source['enabled'] else "✗")
            enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sources_table.setItem(row, 0, enabled_item)
            
            # URI column
            uri_item = QTableWidgetItem(source.get('uri', ''))
            self.sources_table.setItem(row, 1, uri_item)
            
            # Suite column
            suite_item = QTableWidgetItem(source.get('suite', '').replace(' ', '\n'))
            self.sources_table.setItem(row, 2, suite_item)
            
            # Components column
            components_item = QTableWidgetItem(source.get('components', '').replace(' ', '\n'))
            self.sources_table.setItem(row, 3, components_item)
            
            # Gray out disabled rows
            if not source['enabled']:
                for col in range(4):
                    item = self.sources_table.item(row, col)
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)
        
        if self.logger:
            self.logger.info(f"Loaded {len(sources)} APT sources")
    
    def _parse_sources(self):
        """Parse APT sources from files"""
        sources = []
        
        # Parse main sources.list
        sources_list_path = '/etc/apt/sources.list'
        if os.path.exists(sources_list_path):
            sources.extend(self._parse_sources_file(sources_list_path))
        
        # Parse sources.list.d directory
        sources_d = '/etc/apt/sources.list.d'
        if os.path.isdir(sources_d):
            for filename in sorted(os.listdir(sources_d)):
                if filename.endswith('.list') or filename.endswith('.sources'):
                    filepath = os.path.join(sources_d, filename)
                    sources.extend(self._parse_sources_file(filepath))
        
        return sources
    
    def _parse_sources_file(self, filepath):
        """Parse a single sources file (.list or .sources format)"""
        if filepath.endswith('.sources'):
            return self._parse_deb822_format(filepath)
        else:
            return self._parse_one_line_format(filepath)
    
    def _parse_one_line_format(self, filepath):
        """Parse one-line-style format (.list files)"""
        sources = []
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                enabled = not line.startswith('#')
                clean_line = line.lstrip('#').strip()
                
                if clean_line.startswith('deb'):
                    # Remove options in brackets
                    if '[' in clean_line:
                        bracket_start = clean_line.index('[')
                        bracket_end = clean_line.index(']', bracket_start)
                        clean_line = clean_line[:bracket_start] + clean_line[bracket_end+1:]
                    
                    parts = clean_line.split()
                    if len(parts) >= 3:
                        uri = parts[1]
                        suite = parts[2]
                        components = ' '.join(parts[3:]) if len(parts) > 3 else ''
                        
                        sources.append({
                            'file': filepath,
                            'line': line_num,
                            'enabled': enabled,
                            'uri': uri,
                            'suite': suite,
                            'components': components,
                            'raw': line
                        })
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing {filepath}: {e}")
        return sources
    
    def _parse_deb822_format(self, filepath):
        """Parse DEB822 format (.sources files)"""
        sources = []
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Split into stanzas (separated by blank lines)
            stanzas = content.split('\n\n')
            
            for stanza in stanzas:
                if not stanza.strip():
                    continue
                
                fields = {}
                has_field = False
                all_fields_commented = True
                
                for line in stanza.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip pure comment lines (no colon)
                    if line.startswith('#'):
                        if ':' not in line:
                            continue
                        # Field line is commented
                        line = line.lstrip('#').strip()
                    else:
                        # Found at least one uncommented field
                        if ':' in line:
                            all_fields_commented = False
                    
                    if ':' in line:
                        has_field = True
                        key, value = line.split(':', 1)
                        fields[key.strip()] = value.strip()
                
                if has_field and 'Types' in fields and 'URIs' in fields:
                    sources.append({
                        'file': filepath,
                        'line': 1,
                        'enabled': not all_fields_commented,
                        'uri': fields.get('URIs', ''),
                        'suite': fields.get('Suites', ''),
                        'components': fields.get('Components', ''),
                        'raw': stanza
                    })
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing {filepath}: {e}")
        return sources
