from dataclasses import dataclass
from typing import Optional, Dict, Any
import sqlite3
import json
import time
from cache.database import DatabaseManager

@dataclass
class RatingCache:
    """Rating cache data structure"""
    app_id: str
    rating: float
    review_count: int
    star_counts: str  # JSON string of star distribution
    cached_at: float
    
class RatingCacheModel:
    """Model for managing rating cache in SQLite database"""
    
    def __init__(self, logging_service=None):
        self.db_manager = DatabaseManager()
        self.logging_service = logging_service
        
        if self.logging_service:
            self.logger = self.logging_service.get_logger('rating_cache')
        else:
            import logging
            self.logger = logging.getLogger('rating_cache')
        
        self._ensure_table_exists()
        self.logger.debug("Rating cache model initialized")
    
    def _ensure_table_exists(self):
        """Create rating cache table if it doesn't exist"""
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rating_cache (
                    app_id TEXT PRIMARY KEY,
                    rating REAL NOT NULL,
                    review_count INTEGER NOT NULL,
                    star_counts TEXT NOT NULL,
                    cached_at REAL NOT NULL
                )
            """)
            conn.commit()
    
    def get_rating(self, app_id: str, ttl: int = 3600) -> Optional[RatingCache]:
        """Get cached rating if not expired"""
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.execute(
                "SELECT app_id, rating, review_count, star_counts, cached_at FROM rating_cache WHERE app_id = ?",
                (app_id,)
            )
            row = cursor.fetchone()
            
            if row:
                rating_cache = RatingCache(*row)
                # Check if expired
                if time.time() - rating_cache.cached_at < ttl:
                    self.logger.debug(f"Cache hit for {app_id}: {rating_cache.rating}/5")
                    return rating_cache
                else:
                    # Remove expired entry
                    self.logger.debug(f"Cache expired for {app_id}, removing")
                    self.delete_rating(app_id)
            else:
                self.logger.debug(f"Cache miss for {app_id}")
        
        return None
    
    def set_rating(self, app_id: str, rating: float, review_count: int, star_counts: Dict[int, int]):
        """Cache rating data"""
        star_counts_json = json.dumps(star_counts)
        cached_at = time.time()
        
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO rating_cache 
                (app_id, rating, review_count, star_counts, cached_at)
                VALUES (?, ?, ?, ?, ?)
            """, (app_id, rating, review_count, star_counts_json, cached_at))
            conn.commit()
        
        self.logger.debug(f"Cached rating for {app_id}: {rating}/5 ({review_count} reviews)")
    
    def set_no_rating(self, app_id: str):
        """Cache that an app has no rating available"""
        cached_at = time.time()
        
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO rating_cache 
                (app_id, rating, review_count, star_counts, cached_at)
                VALUES (?, ?, ?, ?, ?)
            """, (app_id, 0.0, 0, '{}', cached_at))
            conn.commit()
        
        self.logger.debug(f"Cached no rating available for {app_id}")
    
    def delete_rating(self, app_id: str):
        """Delete cached rating"""
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("DELETE FROM rating_cache WHERE app_id = ?", (app_id,))
            conn.commit()
    
    def clear_expired(self, ttl: int = 3600):
        """Clear all expired ratings"""
        cutoff_time = time.time() - ttl
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("DELETE FROM rating_cache WHERE cached_at < ?", (cutoff_time,))
            conn.commit()
    
    def clear_all(self):
        """Clear all cached ratings"""
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("DELETE FROM rating_cache")
            conn.commit()