# Plugin Implementation Example

## Complete Example: Snap Plugin

This example shows a complete implementation of a Snap backend plugin.

> **Note**: For plugin-specific documentation (features, configuration, troubleshooting), see the [plugins documentation directory](../plugins/). This example focuses on implementation patterns.

### File: `src/controllers/plugins/snap_plugin.py`

```python
from controllers.base_controller import BasePackageController
from models.package_model import Package
from typing import List, Set, Dict, Optional
import subprocess
import json
import shutil

class SnapPlugin(BasePackageController):
    """Snap package manager backend plugin"""
    
    def __init__(self, connection_manager=None, logging_service=None):
        from settings.app_settings import AppSettings
        
        self.connection_manager = connection_manager
        self.logging_service = logging_service
        self.logger = logging_service.get_logger('snap') if logging_service else None
        
        # Load settings
        self.settings = AppSettings()
        self.default_channel = self.settings.get('snap.channel', 'stable')
        self.allow_classic = self.settings.get('snap.classic_confinement', False)
    
    # === Identity & Availability ===
    
    @property
    def backend_id(self) -> str:
        return 'snap'
    
    @property
    def display_name(self) -> str:
        return 'Snap Packages'
    
    def is_available(self) -> bool:
        """Check if snapd is installed and running"""
        if not shutil.which('snap'):
            return False
        
        try:
            # Check if snapd is running
            result = subprocess.run(
                ['snap', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_capabilities(self) -> Set[str]:
        return {
            'search',
            'install',
            'remove',
            'update',
            'list_installed',
            'list_updates',
            'categories'
        }
    
    # === Core Operations ===
    
    def search_packages(self, query: str) -> List[Package]:
        """Search Snap store for packages"""
        if self.logger:
            self.logger.info(f"Searching Snap store: {query}")
        
        try:
            result = subprocess.run(
                ['snap', 'find', query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            packages = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    version = parts[1]
                    publisher = parts[2]
                    description = ' '.join(parts[3:])
                    
                    package = Package(
                        name=name,
                        version=version,
                        description=description,
                        backend='snap'
                    )
                    package.metadata = {
                        'publisher': publisher,
                        'store': 'snapcraft'
                    }
                    packages.append(package)
            
            if self.logger:
                self.logger.info(f"Found {len(packages)} Snap packages")
            
            return packages
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Snap search failed: {e}")
            return []
    
    def install_package(self, package_id: str) -> bool:
        """Install a Snap package"""
        if self.logger:
            self.logger.info(f"Installing Snap package: {package_id}")
        
        try:
            # Use pkexec for privilege escalation
            result = subprocess.run(
                ['pkexec', 'snap', 'install', package_id],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            
            if success and self.logger:
                self.logger.info(f"Successfully installed: {package_id}")
            elif self.logger:
                self.logger.error(f"Failed to install {package_id}: {result.stderr}")
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Snap install error: {e}")
            return False
    
    def remove_package(self, package_id: str) -> bool:
        """Remove a Snap package"""
        if self.logger:
            self.logger.info(f"Removing Snap package: {package_id}")
        
        try:
            result = subprocess.run(
                ['pkexec', 'snap', 'remove', package_id],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            
            if success and self.logger:
                self.logger.info(f"Successfully removed: {package_id}")
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Snap remove error: {e}")
            return False
    
    def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[Package]:
        """Get list of installed Snap packages"""
        if self.logger:
            self.logger.info("Fetching installed Snap packages")
        
        try:
            result = subprocess.run(
                ['snap', 'list', '--unicode=never'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            packages = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    version = parts[1]
                    rev = parts[2]
                    
                    package = Package(
                        name=name,
                        version=version,
                        description=f"Snap package (rev {rev})",
                        backend='snap'
                    )
                    package.metadata = {
                        'revision': rev,
                        'installed': True
                    }
                    packages.append(package)
            
            # Apply pagination
            if limit:
                packages = packages[offset:offset + limit]
            
            if self.logger:
                self.logger.info(f"Found {len(packages)} installed Snap packages")
            
            return packages
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to list Snap packages: {e}")
            return []
    
    # === Optional Operations ===
    
    def get_upgradable_packages(self) -> List[Dict]:
        """Get Snap packages with available updates"""
        if self.logger:
            self.logger.info("Checking for Snap updates")
        
        try:
            result = subprocess.run(
                ['snap', 'refresh', '--list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            updates = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    update_info = {
                        'name': parts[0],
                        'current_version': parts[1],
                        'new_version': parts[2],
                        'description': f"Snap package update available",
                        'is_security': False,
                        'backend': 'snap'
                    }
                    updates.append(update_info)
            
            if self.logger:
                self.logger.info(f"Found {len(updates)} Snap updates")
            
            return updates
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to check Snap updates: {e}")
            return []
    
    def update_package(self, package_id: str) -> bool:
        """Update a single Snap package"""
        if self.logger:
            self.logger.info(f"Updating Snap package: {package_id}")
        
        try:
            result = subprocess.run(
                ['pkexec', 'snap', 'refresh', package_id],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return result.returncode == 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Snap update error: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """Get Snap store categories"""
        # Snap doesn't have a direct category API, return common categories
        return [
            'productivity',
            'development',
            'utilities',
            'games',
            'social',
            'entertainment',
            'education',
            'server-and-cloud'
        ]
    
    def get_packages_by_category(self, category: str) -> List[Package]:
        """Get packages in a category (via search)"""
        # Snap doesn't have category filtering, use search as approximation
        return self.search_packages(category)
    
    # === Category Mapping ===
    
    def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
        """Map sidebar categories to Snap categories"""
        return {
            'games': ['games'],
            'graphics': ['photo-and-video'],
            'internet': ['social', 'communication'],
            'multimedia': ['music-and-audio', 'photo-and-video'],
            'office': ['productivity', 'finance'],
            'development': ['development'],
            'system': ['server-and-cloud', 'devices-and-iot'],
            'utilities': ['utilities'],
            'education': ['education', 'books-and-reference'],
            'science': ['science'],
        }
    
    def map_to_sidebar_category(self, snap_category: str) -> Optional[str]:
        """Map Snap category to sidebar category"""
        mapping = self.get_sidebar_category_mapping()
        for sidebar_cat, snap_cats in mapping.items():
            if snap_category.lower() in [c.lower() for c in snap_cats]:
                return sidebar_cat
        return None
    
    # === Settings Integration ===
    
    def get_settings_schema(self) -> Dict:
        """Snap plugin settings"""
        return {
            'channel': {
                'type': 'list',
                'label': 'Default Channel',
                'default': 'stable',
                'description': 'Default channel for snap installations',
                'options': ['stable', 'candidate', 'beta', 'edge']
            },
            'classic_confinement': {
                'type': 'bool',
                'label': 'Allow Classic Confinement',
                'default': False,
                'description': 'Allow installation of snaps with classic confinement'
            },
            'auto_refresh': {
                'type': 'bool',
                'label': 'Auto-refresh Snaps',
                'default': True,
                'description': 'Automatically refresh snaps in background'
            }
        }
    
    def on_settings_changed(self, setting_key: str, value):
        """Handle setting changes"""
        if self.logger:
            self.logger.info(f"Snap setting changed: {setting_key} = {value}")
        
        if setting_key == 'channel':
            self.default_channel = value
        elif setting_key == 'classic_confinement':
            self.allow_classic = value
```

## Testing the Plugin

### Unit Tests: `tests/test_snap_plugin.py`

```python
import unittest
from unittest.mock import Mock, patch
from controllers.plugins.snap_plugin import SnapPlugin

class TestSnapPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = SnapPlugin()
    
    def test_backend_id(self):
        self.assertEqual(self.plugin.backend_id, 'snap')
    
    def test_display_name(self):
        self.assertEqual(self.plugin.display_name, 'Snap Packages')
    
    def test_capabilities(self):
        caps = self.plugin.get_capabilities()
        self.assertIn('search', caps)
        self.assertIn('install', caps)
        self.assertIn('remove', caps)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_is_available_true(self, mock_run, mock_which):
        mock_which.return_value = '/usr/bin/snap'
        mock_run.return_value = Mock(returncode=0)
        
        self.assertTrue(self.plugin.is_available())
    
    @patch('shutil.which')
    def test_is_available_false(self, mock_which):
        mock_which.return_value = None
        
        self.assertFalse(self.plugin.is_available())
    
    @patch('subprocess.run')
    def test_search_packages(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Name  Version  Publisher  Notes  Summary\nfirefox  95.0  mozilla✓  -  Web browser\n"
        )
        
        results = self.plugin.search_packages('firefox')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'firefox')
        self.assertEqual(results[0].backend, 'snap')

if __name__ == '__main__':
    unittest.main()
```

## Integration with PackageManager

Once the plugin is created, it's automatically discovered:

```python
# In PackageManager._discover_plugins()
from controllers.plugins.snap_plugin import SnapPlugin

snap = SnapPlugin(self.connection_manager, self.logging_service)
self.register_backend(snap)
```

## Usage in Views

```python
# Search across all backends including Snap
results = self.package_manager.search_packages('firefox')

# Search only Snap
results = self.package_manager.search_packages('firefox', backend='snap')

# Install from Snap
self.package_manager.install_package('firefox', backend='snap')

# Check if Snap backend is available
if 'snap' in self.package_manager.backends:
    print("Snap support enabled")
```

## Plugin Metadata (Optional)

Add metadata for better plugin management:

```python
class SnapPlugin(BasePackageController):
    # Plugin metadata
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_AUTHOR = "Apt-Ex Team"
    PLUGIN_DESCRIPTION = "Snap package manager integration"
    PLUGIN_REQUIRES = ["snapd >= 2.0"]
    
    @classmethod
    def get_metadata(cls) -> Dict:
        return {
            'version': cls.PLUGIN_VERSION,
            'author': cls.PLUGIN_AUTHOR,
            'description': cls.PLUGIN_DESCRIPTION,
            'requires': cls.PLUGIN_REQUIRES
        }
```
