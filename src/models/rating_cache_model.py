from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import time
from cache import LMDBManager

@dataclass
class RatingCache:
    """Rating cache data structure"""
    app_id: str
    rating: float
    review_count: int
    star_counts: str  # JSON string of star distribution
    cached_at: float
    
class RatingCacheModel:
    """Model for managing rating cache in LMDB database"""
    
    def __init__(self, lmdb_manager: LMDBManager, logging_service=None):
        self.lmdb = lmdb_manager
        self.db_name = 'metadata'
        self.logging_service = logging_service
        
        if self.logging_service:
            self.logger = self.logging_service.get_logger('rating_cache')
        else:
            import logging
            self.logger = logging.getLogger('rating_cache')
        
        self.logger.debug("Rating cache model initialized")
    
    def get_rating(self, app_id: str, ttl: int = 3600) -> Optional[RatingCache]:
        """Get cached rating if not expired"""
        key = f"rating:{app_id}"
        data = self.lmdb.get(self.db_name, key)
        
        if data:
            rating_cache = RatingCache(**data)
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
        
        key = f"rating:{app_id}"
        data = {
            'app_id': app_id,
            'rating': rating,
            'review_count': review_count,
            'star_counts': star_counts_json,
            'cached_at': cached_at
        }
        self.lmdb.put(self.db_name, key, data)
        
        self.logger.debug(f"Cached rating for {app_id}: {rating}/5 ({review_count} reviews)")
    
    def set_no_rating(self, app_id: str):
        """Cache that an app has no rating available"""
        cached_at = time.time()
        
        key = f"rating:{app_id}"
        data = {
            'app_id': app_id,
            'rating': 0.0,
            'review_count': 0,
            'star_counts': '{}',
            'cached_at': cached_at
        }
        self.lmdb.put(self.db_name, key, data)
        
        self.logger.debug(f"Cached no rating available for {app_id}")
    
    def delete_rating(self, app_id: str):
        """Delete cached rating"""
        key = f"rating:{app_id}"
        self.lmdb.delete(self.db_name, key)
    
    def clear_expired(self, ttl: int = 3600):
        """Clear all expired ratings"""
        try:
            cutoff_time = time.time() - ttl
            db = self.lmdb.get_db(self.db_name)
            
            with self.lmdb.transaction(write=True) as txn:
                cursor = txn.cursor(db=db)
                keys_to_delete = []
                
                for key, value in cursor:
                    if key.startswith(b'rating:'):
                        data = json.loads(value.decode())
                        if data.get('cached_at', 0) < cutoff_time:
                            keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    txn.delete(key, db=db)
        except Exception:
            pass
    
    def clear_all(self):
        """Clear all cached ratings"""
        db = self.lmdb.get_db(self.db_name)
        
        with self.lmdb.transaction(write=True) as txn:
            cursor = txn.cursor(db=db)
            keys_to_delete = []
            
            for key, _ in cursor:
                if key.startswith(b'rating:'):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                txn.delete(key, db=db)