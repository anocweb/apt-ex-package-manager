import sqlite3
import threading
import queue
from contextlib import contextmanager
from typing import Optional

class SQLiteConnectionManager:
    """Thread-safe SQLite connection manager with pooling"""
    
    def __init__(self, db_path: str, pool_size: int = 5, logging_service=None):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._thread_local = threading.local()
        self._lock = threading.Lock()
        self._closed = False
        self.logger = logging_service.get_logger('db.connection') if logging_service else None
        
        # Query statistics
        self.query_count = 0
        self.query_times = []
        self.stats_start_time = None
        
        if self.logger:
            self.logger.info(f"Initializing connection pool: {pool_size} connections to {db_path}")
        
        # Pre-warm connection pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create initial connections with optimized settings"""
        for i in range(self.pool_size):
            conn = self._create_connection()
            self._pool.put(conn)
        
        if self.logger:
            self.logger.debug(f"Connection pool initialized with {self.pool_size} connections")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized SQLite connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        
        # Optimize SQLite settings
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=10000')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.execute('PRAGMA busy_timeout=30000')
        
        return conn
    
    def get_connection(self) -> sqlite3.Connection:
        """Get connection from pool or create new one"""
        if self._closed:
            raise RuntimeError("Connection manager is closed")
        
        # Try thread-local connection first
        if hasattr(self._thread_local, 'connection'):
            return self._thread_local.connection
        
        try:
            # Get from pool (non-blocking)
            conn = self._pool.get_nowait()
            self._thread_local.connection = conn
            return conn
        except queue.Empty:
            # Pool exhausted, create temporary connection
            if self.logger:
                self.logger.warning(f"Connection pool exhausted, creating temporary connection")
            return self._create_connection()
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        if self._closed:
            conn.close()
            return
        
        # Clear thread-local reference
        if hasattr(self._thread_local, 'connection'):
            delattr(self._thread_local, 'connection')
        
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool full, close excess connection
            conn.close()
    
    @contextmanager
    def transaction(self, isolation_level: Optional[str] = None):
        """Managed transaction context"""
        import time
        conn = self.get_connection()
        old_isolation = conn.isolation_level
        start_time = time.time()
        
        try:
            # Set isolation level to enable transactions
            conn.isolation_level = isolation_level if isolation_level else 'DEFERRED'
            yield conn
            conn.commit()
            
            # Track query stats
            elapsed = time.time() - start_time
            self._record_query(elapsed)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.isolation_level = old_isolation
            self.return_connection(conn)
    
    @contextmanager
    def connection(self):
        """Simple connection context (auto-commit)"""
        import time
        conn = self.get_connection()
        start_time = time.time()
        
        try:
            yield conn
            
            # Track query stats
            elapsed = time.time() - start_time
            self._record_query(elapsed)
        finally:
            self.return_connection(conn)
    
    def _record_query(self, elapsed_time: float):
        """Record query execution time"""
        import time
        if self.stats_start_time is None:
            self.stats_start_time = time.time()
        
        self.query_count += 1
        self.query_times.append(elapsed_time)
        
        # Keep only last 1000 query times
        if len(self.query_times) > 1000:
            self.query_times = self.query_times[-1000:]
    
    def get_active_connections(self) -> int:
        """Get number of active connections (not in pool)"""
        return self.pool_size - self._pool.qsize()
    
    def get_query_stats(self) -> dict:
        """Get query statistics"""
        import time
        if not self.query_times:
            return {'qps': 0, 'min': 0, 'max': 0, 'avg': 0}
        
        elapsed = time.time() - self.stats_start_time if self.stats_start_time else 1
        qps = self.query_count / elapsed if elapsed > 0 else 0
        
        return {
            'qps': qps,
            'min': min(self.query_times) * 1000,  # Convert to ms
            'max': max(self.query_times) * 1000,
            'avg': sum(self.query_times) / len(self.query_times) * 1000
        }
    
    def close_all(self):
        """Close all pooled connections"""
        self._closed = True
        closed_count = 0
        
        # Close thread-local connections
        if hasattr(self._thread_local, 'connection'):
            self._thread_local.connection.close()
            closed_count += 1
        
        # Close pooled connections
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
                closed_count += 1
            except queue.Empty:
                break
        
        if self.logger:
            self.logger.info(f"Connection manager closed, {closed_count} connections closed")