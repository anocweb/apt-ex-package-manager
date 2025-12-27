from PyQt6.QtCore import pyqtSignal
from widgets.base_list_item import BaseListItem
from services.odrs_service import ODRSService


class PackageListItem(BaseListItem):
    """Reusable KDE Discover-style package list item widget"""
    
    install_requested = pyqtSignal(str)
    
    def __init__(self, package, odrs_service=None, parent=None):
        self.package = package
        self.odrs_service = odrs_service or ODRSService()
        super().__init__('widgets/package_list_item.ui', parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup package-specific UI"""
        # Set package data
        self.nameLabel.setText(getattr(self.package, 'name', 'Unknown Package'))
        self.descLabel.setText(getattr(self.package, 'description', 'No description available'))
        self.backendLabel.setText(getattr(self.package, 'backend', 'apt').upper())
        
        # Connect install button
        self.installButton.clicked.connect(lambda: self.install_requested.emit(getattr(self.package, 'name', '')))
        
        # Apply dev outline
        self._apply_dev_outline(self.iconLabel, self.nameLabel, self.descLabel, 
                                self.ratingLabel, self.backendLabel, self.installButton)
        
        # Update rating display
        if not self.dev_outline:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.update_rating_display)
    
    def update_rating_display(self):
        """Update rating display with fresh data"""
        rating_text = self._get_rating_text()
        self.ratingLabel.setText(rating_text)
    
    def _get_rating_text(self) -> str:
        """Get formatted rating text from ODRS"""
        from settings.app_settings import AppSettings
        import sys
        
        # Skip rating lookups when dev logging is active
        if '--dev-logging' in sys.argv:
            return '<span style="color: palette(mid);">Dev Mode</span>'
        
        # State 1: ODRS disabled
        settings = AppSettings()
        if not settings.get_odrs_enabled():
            return '<span style="color: palette(mid);">Ratings Disabled</span>'
        
        # State 2: No ODRS service available
        if not self.odrs_service:
            return '<span style="color: palette(window-text);">Collecting rating...</span>'
        
        try:
            # Check if rating is already included in package summary
            if hasattr(self.package, 'rating') and self.package.rating is not None:
                rating_val = self.package.rating
                review_count = getattr(self.package, 'review_count', 0)
                
                if review_count > 0:
                    filled_stars = int(rating_val)
                    empty_stars = 5 - filled_stars
                    stars_html = (
                        f'<span style="color: #FFD700;">{"★" * filled_stars}</span>' +
                        f'<span style="color: #B8860B;">{"☆" * empty_stars}</span>'
                    )
                    return f'{stars_html}<span style="color: palette(window-text);"> {rating_val} ({review_count} reviews)</span>'
                else:
                    empty_stars = '☆' * 5
                    return f'<span style="color: #B8860B;">{empty_stars}</span><span style="color: palette(mid);"> No Ratings Available</span>'
            
            # Fallback to ODRS service lookup
            package_name = getattr(self.package, 'name', '')
            app_id = self.odrs_service.map_package_to_app_id(package_name)
            rating = self.odrs_service._get_cached_rating(app_id)
            
            if rating is None:
                return '<span style="color: palette(window-text);">Collecting rating...</span>'
            elif rating.review_count > 0:
                filled_stars = int(rating.rating)
                empty_stars = 5 - filled_stars
                stars_html = (
                    f'<span style="color: #FFD700;">{"★" * filled_stars}</span>' +
                    f'<span style="color: #B8860B;">{"☆" * empty_stars}</span>'
                )
                return f'{stars_html}<span style="color: palette(window-text);"> {rating.rating} ({rating.review_count} reviews)</span>'
            else:
                empty_stars = '☆' * 5
                return f'<span style="color: #B8860B;">{empty_stars}</span><span style="color: palette(mid);"> No Ratings Available</span>'
        except Exception:
            return '<span style="color: palette(window-text);">Collecting rating...</span>'