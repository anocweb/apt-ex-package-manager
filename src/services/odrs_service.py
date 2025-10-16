import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
import time
from PyQt6.QtCore import QThread, pyqtSignal

@dataclass
class PackageRating:
    """Package rating data from ODRS"""
    app_id: str
    rating: float  # 0-5 stars
    review_count: int
    star_counts: Dict[int, int]  # {1: count, 2: count, ...}

class ODRSWorker(QThread):
    """Worker thread for fetching ODRS ratings"""
    ratings_fetched = pyqtSignal(dict)  # {app_id: PackageRating}
    
    def __init__(self, app_ids, odrs_service):
        super().__init__()
        self.app_ids = app_ids
        self.odrs_service = odrs_service
    
    def run(self):
        ratings = self.odrs_service._fetch_ratings_sync(self.app_ids)
        self.ratings_fetched.emit(ratings)

class ODRSService:
    """Service for fetching package ratings from GNOME ODRS API"""
    
    def __init__(self, status_callback=None, logging_service=None):
        self.base_url = "https://odrs.gnome.org/1.0/reviews/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Apt-Ex-Package-Manager/1.0'
        })
        self.cache_ttl = 3600  # 1 hour
        self.status_callback = status_callback
        self.worker = None
        self.logging_service = logging_service
        
        if self.logging_service:
            self.logger = self.logging_service.get_logger('odrs')
        else:
            import logging
            self.logger = logging.getLogger('odrs')
        
        # Initialize SQLite cache - will be set by MainView
        self.cache_model = None
        self.logger.debug("ODRS service initialized")
    
    def get_ratings_async(self, app_ids: List[str], callback):
        """Fetch ratings asynchronously"""
        if self.worker and self.worker.isRunning():
            self.logger.debug("ODRS worker already running, skipping request")
            return  # Already fetching
        
        self.logger.debug(f"Fetching ratings for {len(app_ids)} apps")
        
        # Check cache first
        results = {}
        uncached_ids = []
        for app_id in app_ids:
            cached = self._get_cached_rating(app_id)
            if cached:
                results[app_id] = cached
            else:
                uncached_ids.append(app_id)
        
        self.logger.debug(f"Found {len(results)} cached ratings, {len(uncached_ids)} need fetching")
        
        if not uncached_ids:
            callback(results)
            return
        
        # Show status
        if self.status_callback:
            self.status_callback(f"Fetching ratings for {len(uncached_ids)} packages...")
        
        self.logger.info(f"Starting async fetch for {len(uncached_ids)} uncached ratings")
        
        # Start worker thread
        self.worker = ODRSWorker(uncached_ids, self)
        self.worker.ratings_fetched.connect(lambda ratings: self._on_ratings_fetched(ratings, results, callback))
        self.worker.start()
    
    def _on_ratings_fetched(self, new_ratings, existing_results, callback):
        """Handle ratings fetched from worker thread"""
        if self.status_callback:
            self.status_callback("")
        
        self.logger.info(f"Received {len(new_ratings)} new ratings from worker thread")
        
        # Merge results
        existing_results.update(new_ratings)
        callback(existing_results)
    
    def _fetch_ratings_sync(self, app_ids: List[str]) -> Dict[str, PackageRating]:
        """Synchronous rating fetch for worker thread"""
        results = {}
        try:
            self.logger.debug(f"Making ODRS API request for {len(app_ids)} apps")
            response = self.session.get(
                f"{self.base_url}/ratings",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"ODRS API returned data for {len(data)} total apps")
            
            found_ratings = 0
            no_ratings = 0
            
            for app_id in app_ids:
                if app_id in data:
                    rating_data = data[app_id]
                    if rating_data and 'total' in rating_data:
                        rating = self._parse_rating_data(app_id, rating_data)
                        results[app_id] = rating
                        self._cache_rating(app_id, rating)
                        found_ratings += 1
                        self.logger.debug(f"Found rating for {app_id}: {rating.rating}/5 ({rating.review_count} reviews)")
                    else:
                        # Cache that this app has no rating
                        self.cache_model.set_no_rating(app_id)
                        no_ratings += 1
                else:
                    # Cache that this app has no rating
                    self.cache_model.set_no_rating(app_id)
                    no_ratings += 1
            
            self.logger.info(f"ODRS fetch complete: {found_ratings} with ratings, {no_ratings} without ratings")
            
        except Exception as e:
            self.logger.error(f"ODRS API error: {e}")
        
        return results
    
    def get_ratings(self, app_ids: List[str]) -> Dict[str, PackageRating]:
        """Fetch ratings synchronously (for compatibility)"""
        return self._fetch_ratings_sync(app_ids)
    
    def get_single_rating(self, app_id: str) -> Optional[PackageRating]:
        """Fetch rating for a single app ID"""
        ratings = self.get_ratings([app_id])
        return ratings.get(app_id)
    
    def _parse_rating_data(self, app_id: str, data: dict) -> PackageRating:
        """Parse ODRS rating data into PackageRating object"""
        # ODRS uses star0, star1, star2, star3, star4, star5
        total_reviews = data.get('total', 0)
        
        if total_reviews == 0:
            return PackageRating(app_id=app_id, rating=0, review_count=0, star_counts={})
        
        # Calculate weighted average (star0 is ignored, star1-star5 are 1-5 stars)
        weighted_sum = 0
        star_counts = {}
        
        for star in range(1, 6):  # 1-5 stars
            count = data.get(f'star{star}', 0)
            star_counts[star] = count
            weighted_sum += star * count
        
        average_rating = weighted_sum / total_reviews if total_reviews > 0 else 0
        
        return PackageRating(
            app_id=app_id,
            rating=round(average_rating, 1),
            review_count=total_reviews,
            star_counts=star_counts
        )
    
    def _get_cached_rating(self, app_id: str) -> Optional[PackageRating]:
        """Get rating from SQLite cache if not expired"""
        cached = self.cache_model.get_rating(app_id, self.cache_ttl)
        if cached:
            import json
            star_counts = json.loads(cached.star_counts)
            return PackageRating(
                app_id=cached.app_id,
                rating=cached.rating,
                review_count=cached.review_count,
                star_counts=star_counts
            )
        return None
    
    def _cache_rating(self, app_id: str, rating: PackageRating):
        """Cache rating to SQLite database"""
        self.cache_model.set_rating(
            app_id=app_id,
            rating=rating.rating,
            review_count=rating.review_count,
            star_counts=rating.star_counts
        )
    
    def map_package_to_app_id(self, package_name: str) -> str:
        """Map APT package name to ODRS app ID"""
        # Based on actual ODRS data, use desktop file names or app IDs
        mappings = {
            'firefox': 'org.mozilla.Firefox',
            'firefox-esr': 'firefox-esr.desktop',
            'thunderbird': 'thunderbird.desktop',
            'libreoffice': 'libreoffice-startcenter.desktop',
            'gimp': 'gimp.desktop',
            'vlc': 'vlc.desktop',
            'code': 'code.desktop',
            'chromium-browser': 'chromium.desktop',
            'blender': 'blender.desktop',
            'inkscape': 'inkscape.desktop',
            'audacity': 'audacity.desktop',
            'obs-studio': 'obs.desktop',
            'steam': 'steam.desktop',
            'discord': 'discord.desktop',
            'telegram-desktop': 'telegram.desktop',
            'spotify-client': 'spotify.desktop'
        }
        
        return mappings.get(package_name, f"{package_name}.desktop")