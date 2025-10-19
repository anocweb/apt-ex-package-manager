"""About panel controller"""
from .base_panel import BasePanel


class AboutPanel(BasePanel):
    """Panel for about information"""
    
    def get_title(self):
        """Return panel title"""
        return "About Apt-Ex Package Manager"
