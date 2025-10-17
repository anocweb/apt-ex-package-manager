from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic
from services.odrs_service import ODRSService

class PackageListItem(QFrame):
    """Reusable KDE Discover-style package list item widget"""
    
    install_requested = pyqtSignal(str)  # Emits package name when install is clicked
    
    def __init__(self, package, odrs_service=None, parent=None):
        super().__init__(parent)
        self.package = package
        self.odrs_service = odrs_service or ODRSService()
        uic.loadUi('src/ui/package_list_item.ui', self)
        self.setup_ui()
    
    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Check if dev outline is active
        from PyQt6.QtWidgets import QApplication
        app_stylesheet = QApplication.instance().styleSheet()
        dev_outline = "border: 1px solid red" in app_stylesheet
        
        if dev_outline:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid red;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid palette(mid);
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        
        # Set package data
        name = getattr(self.package, 'name', 'Unknown Package')
        self.nameLabel.setText(name)
        
        description = getattr(self.package, 'description', 'No description available')
        self.descLabel.setText(description)
        
        backend = getattr(self.package, 'backend', 'apt')
        self.backendLabel.setText(backend.upper())
        
        # Connect install button
        package_name = getattr(self.package, 'name', '')
        self.installButton.clicked.connect(lambda: self.install_requested.emit(package_name))
        
        # Apply dev outline if active
        if dev_outline:
            self.iconLabel.setStyleSheet(self.iconLabel.styleSheet() + "; border: 1px solid red;")
            self.nameLabel.setStyleSheet(self.nameLabel.styleSheet() + "; border: 1px solid red;")
            self.descLabel.setStyleSheet(self.descLabel.styleSheet() + "; border: 1px solid red;")
            self.ratingLabel.setStyleSheet(self.ratingLabel.styleSheet() + "; border: 1px solid red;")
            self.backendLabel.setStyleSheet(self.backendLabel.styleSheet() + "; border: 1px solid red;")
            self.installButton.setStyleSheet(self.installButton.styleSheet().replace("border: none;", "border: 1px solid red;"))
        
        # Set transparent for mouse events
        for label in [self.nameLabel, self.descLabel, self.ratingLabel, self.backendLabel]:
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        # Update rating display
        if not dev_outline:
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