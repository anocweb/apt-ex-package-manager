"""About panel controller"""
from .base_panel import BasePanel

try:
    from version import __version__
except ImportError:
    # Fallback for development or if version module not found
    __version__ = "0.1.0"


class AboutPanel(BasePanel):
    """Panel for about information"""
    
    def setup_ui(self):
        """Setup UI components"""
        # Display version if versionLabel exists
        if hasattr(self, 'versionLabel'):
            self.versionLabel.setText(f"Version {__version__}")
    
    def get_title(self):
        """Return panel title"""
        return "About Apt-Ex Package Manager"
