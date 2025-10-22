"""Factory for creating Qt widgets from settings schema"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QCheckBox, QSpinBox, QLineEdit, QComboBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal, QObject
from typing import Dict, Any, Callable


class SettingsWidgetFactory(QObject):
    """Factory to auto-generate Qt widgets from settings schema"""
    
    setting_changed = pyqtSignal(str, object)  # key, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = {}
    
    def create_widget_from_schema(self, schema: Dict, current_values: Dict = None) -> QWidget:
        """Create a widget from settings schema
        
        Args:
            schema: Settings schema dictionary
            current_values: Current setting values
        
        Returns:
            QWidget containing all settings controls
        """
        current_values = current_values or {}
        container = QWidget()
        layout = QFormLayout(container)
        layout.setSpacing(10)
        
        for key, config in schema.items():
            widget = self._create_widget_for_type(key, config, current_values.get(key))
            if widget:
                label = QLabel(config.get('label', key))
                if 'tooltip' in config:
                    label.setToolTip(config['tooltip'])
                    widget.setToolTip(config['tooltip'])
                layout.addRow(label, widget)
                self.widgets[key] = widget
        
        return container
    
    def _create_widget_for_type(self, key: str, config: Dict, current_value: Any) -> QWidget:
        """Create appropriate widget based on type"""
        widget_type = config.get('type', 'string')
        
        if widget_type == 'boolean':
            return self._create_boolean_widget(key, config, current_value)
        elif widget_type == 'integer':
            return self._create_integer_widget(key, config, current_value)
        elif widget_type == 'string':
            return self._create_string_widget(key, config, current_value)
        elif widget_type == 'choice':
            return self._create_choice_widget(key, config, current_value)
        
        return None
    
    def _create_boolean_widget(self, key: str, config: Dict, current_value: Any) -> QCheckBox:
        """Create checkbox for boolean setting"""
        widget = QCheckBox()
        default = config.get('default', False)
        value = current_value if current_value is not None else default
        widget.setChecked(bool(value))
        widget.toggled.connect(lambda checked: self.setting_changed.emit(key, checked))
        return widget
    
    def _create_integer_widget(self, key: str, config: Dict, current_value: Any) -> QSpinBox:
        """Create spinbox for integer setting"""
        widget = QSpinBox()
        widget.setMinimum(config.get('min', 0))
        widget.setMaximum(config.get('max', 999999))
        
        if 'suffix' in config:
            widget.setSuffix(config['suffix'])
        
        default = config.get('default', 0)
        value = current_value if current_value is not None else default
        widget.setValue(int(value))
        widget.valueChanged.connect(lambda val: self.setting_changed.emit(key, val))
        return widget
    
    def _create_string_widget(self, key: str, config: Dict, current_value: Any) -> QLineEdit:
        """Create line edit for string setting"""
        widget = QLineEdit()
        
        if 'placeholder' in config:
            widget.setPlaceholderText(config['placeholder'])
        
        if config.get('password', False):
            widget.setEchoMode(QLineEdit.EchoMode.Password)
        
        default = config.get('default', '')
        value = current_value if current_value is not None else default
        widget.setText(str(value))
        widget.textChanged.connect(lambda text: self.setting_changed.emit(key, text))
        return widget
    
    def _create_choice_widget(self, key: str, config: Dict, current_value: Any) -> QComboBox:
        """Create combobox for choice setting"""
        widget = QComboBox()
        choices = config.get('choices', [])
        widget.addItems(choices)
        
        default = config.get('default', choices[0] if choices else '')
        value = current_value if current_value is not None else default
        
        index = widget.findText(str(value))
        if index >= 0:
            widget.setCurrentIndex(index)
        
        widget.currentTextChanged.connect(lambda text: self.setting_changed.emit(key, text))
        return widget
    
    def get_values(self) -> Dict[str, Any]:
        """Get current values from all widgets"""
        values = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                values[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                values[key] = widget.text()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentText()
        return values
