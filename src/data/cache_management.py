"""
Intelligent Cache Management System
Handles data caching with fallback mechanisms, performance monitoring, and cache optimization
"""

import asyncio
import json
import pickle
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import hashlib
import gzip
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from ..shared.interfaces import MarketData

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    expiry_time: Optional[datetime]
    size_bytes: int
    source: str
    quality_score: float


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hit_count: int
    miss_count: int
    total_requests: int
    hit_rate: float
    avg_response_time_ms: float
    cache_size_mb: float
    entry_count: int
    oldest_entry: Optional[datetime]
    newest_entry: Optional[datetime]


class CacheBackend:
    """Abstract base for cache backends"""
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        raise NotImplementedError
    
    async def set(self, key: str, entry: CacheEntry) -> None:
        raise NotImplementedError
    
    async def delete(self, key: str) -> None:
        raise NotImplementedError
    
    async def clear(self) -> None:
        raise NotImplementedError
    
    async def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size_mb: float = 100.0):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.current_size = 0
        self.lock = threading.RLock()
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.response_times = []
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        start_time = time.time()
        
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.miss_count += 1
                self.response_times.append((time.time() - start_time) * 1000)
                return None
            
            # Check expiry
            if entry.expiry_time and datetime.now() > entry.expiry_time:
                self._remove_entry(key)
                self.miss_count += 1
                self.response_times.append((time.time() - start_time) * 1000)
                return None
            
            # Update access information
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Move to end of access order (most recently used)
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            self.hit_count += 1
            self.response_times.append((time.time() - start_time) * 1000)
            return entry
    
    async def set(self, key: str, entry: CacheEntry) -> None:
        with self.lock:
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Ensure we have space
            await self._ensure_space(entry.size_bytes)
            
            # Add new entry
            self.cache[key] = entry
            self.access_order.append(key)
            self.current_size += entry.size_bytes
    
    async def delete(self, key: str) -> None:
        with self.lock:
            self._remove_entry(key)
    
    async def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_size = 0
    
    async def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0.0
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
            
            oldest_entry = min((e.created_at for e in self.cache.values()), default=None)
            newest_entry = max((e.created_at for e in self.cache.values()), default=None)
            
            return {
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'avg_response_time_ms': avg_response_time,
                'cache_size_mb': self.current_size / (1024 * 1024),
                'entry_count': len(self.cache),
                'oldest_entry': oldest_entry,
                'newest_entry': newest_entry
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update size tracking"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size -= entry.size_bytes
            del self.cache[key]
            
        if key in self.access_order:
            self.access_order.remove(key)
    
    async def _ensure_space(self, needed_bytes: int) -> None:
        """Ensure sufficient space by evicting LRU entries"""
        while (self.current_size + needed_bytes > self.max_size_bytes and 
               self.access_order):
            # Evict least recently used
            lru_key = self.access_order[0]
            self._remove_entry(lru_key)
            logger.debug(f"Evicted LRU cache entry: {lru_key}")


class SQLiteCache(CacheBackend):
    """SQLite-based persistent cache"""
    
    def __init__(self, db_path: Union[str, Path] = "cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.response_times = []
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    data BLOB NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    expiry_time REAL,
                    size_bytes INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    quality_score REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expiry_time ON cache_entries(expiry_time)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        start_time = time.time()
        
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT * FROM cache_entries WHERE key = ?
                    """, (key,))
                    
                    row = cursor.fetchone()
                    if row is None:
                        self.miss_count += 1
                        self.response_times.append((time.time() - start_time) * 1000)
                        return None
                    
                    # Check expiry
                    expiry_time = datetime.fromtimestamp(row['expiry_time']) if row['expiry_time'] else None
                    if expiry_time and datetime.now() > expiry_time:
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                        self.miss_count += 1
                        self.response_times.append((time.time() - start_time) * 1000)
                        return None
                    
                    # Deserialize data
                    try:
                        data = pickle.loads(gzip.decompress(row['data']))
                    except Exception as e:
                        logger.error(f"Failed to deserialize cache entry {key}: {e}")
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                        self.miss_count += 1
                        self.response_times.append((time.time() - start_time) * 1000)
                        return None
                    
                    # Update access information
                    now_timestamp = datetime.now().timestamp()
                    conn.execute("""
                        UPDATE cache_entries 
                        SET last_accessed = ?, access_count = access_count + 1
                        WHERE key = ?
                    """, (now_timestamp, key))
                    
                    entry = CacheEntry(
                        key=row['key'],
                        data=data,
                        created_at=datetime.fromtimestamp(row['created_at']),
                        last_accessed=datetime.now(),
                        access_count=row['access_count'] + 1,
                        expiry_time=expiry_time,
                        size_bytes=row['size_bytes'],
                        source=row['source'],
                        quality_score=row['quality_score']
                    )
                    
                    self.hit_count += 1
                    self.response_times.append((time.time() - start_time) * 1000)
                    return entry
                    
            except Exception as e:
                logger.error(f"Cache get error: {e}")
                self.miss_count += 1
                self.response_times.append((time.time() - start_time) * 1000)
                return None
    
    async def set(self, key: str, entry: CacheEntry) -> None:
        with self.lock:
            try:
                # Serialize data
                serialized_data = gzip.compress(pickle.dumps(entry.data))
                
                with self._get_connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries 
                        (key, data, created_at, last_accessed, access_count, 
                         expiry_time, size_bytes, source, quality_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.key,
                        serialized_data,
                        entry.created_at.timestamp(),
                        entry.last_accessed.timestamp(),
                        entry.access_count,
                        entry.expiry_time.timestamp() if entry.expiry_time else None,
                        len(serialized_data),  # Use actual serialized size
                        entry.source,
                        entry.quality_score
                    ))
                    
            except Exception as e:
                logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str) -> None:
        with self.lock:
            try:
                with self._get_connection() as conn:
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            except Exception as e:
                logger.error(f"Cache delete error: {e}")
    
    async def clear(self) -> None:
        with self.lock:
            try:
                with self._get_connection() as conn:
                    conn.execute("DELETE FROM cache_entries")
            except Exception as e:
                logger.error(f"Cache clear error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            try:
                with self._get_connection() as conn:
                    # Get basic counts
                    cursor = conn.execute("""
                        SELECT 
                            COUNT(*) as entry_count,
                            SUM(size_bytes) as total_size,
                            MIN(created_at) as oldest,
                            MAX(created_at) as newest
                        FROM cache_entries
                    """)
                    row = cursor.fetchone()
                    
                    total_requests = self.hit_count + self.miss_count
                    hit_rate = self.hit_count / total_requests if total_requests > 0 else 0.0
                    avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
                    
                    return {
                        'hit_count': self.hit_count,
                        'miss_count': self.miss_count,
                        'total_requests': total_requests,
                        'hit_rate': hit_rate,
                        'avg_response_time_ms': avg_response_time,
                        'cache_size_mb': (row['total_size'] or 0) / (1024 * 1024),
                        'entry_count': row['entry_count'],
                        'oldest_entry': datetime.fromtimestamp(row['oldest']) if row['oldest'] else None,
                        'newest_entry': datetime.fromtimestamp(row['newest']) if row['newest'] else None
                    }
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
                return {}
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    now_timestamp = datetime.now().timestamp()
                    cursor = conn.execute("""
                        DELETE FROM cache_entries 
                        WHERE expiry_time IS NOT NULL AND expiry_time < ?
                    """, (now_timestamp,))
                    return cursor.rowcount
            except Exception as e:
                logger.error(f"Error cleaning up expired entries: {e}")
                return 0


class IntelligentCacheManager:
    """
    Intelligent cache management with multiple backends, 
    performance monitoring, and adaptive strategies
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Cache configuration
        self.memory_cache_size_mb = self.config.get('memory_cache_size_mb', 50.0)
        self.persistent_cache_path = self.config.get('persistent_cache_path', 'data_cache.db')
        self.default_ttl_hours = self.config.get('default_ttl_hours', 24.0)
        self.max_cache_age_days = self.config.get('max_cache_age_days', 7.0)
        
        # Performance targets
        self.target_hit_rate = self.config.get('target_hit_rate', 0.8)
        self.target_response_time_ms = self.config.get('target_response_time_ms', 50.0)
        
        # Initialize backends
        self.memory_cache = MemoryCache(self.memory_cache_size_mb)
        self.persistent_cache = SQLiteCache(self.persistent_cache_path)
        
        # Monitoring
        self.performance_history = []
        self.last_cleanup_time = datetime.now()
        
        # Background tasks
        self._cleanup_task = None
        self._monitor_task = None
        
    async def get_cached_data(self, location: str) -> Optional[MarketData]:
        """Get cached market data for location"""
        cache_key = self._generate_cache_key(location)
        
        # Try memory cache first
        entry = await self.memory_cache.get(cache_key)
        if entry and isinstance(entry.data, MarketData):
            logger.debug(f"Memory cache hit for {location}")
            return entry.data
        
        # Try persistent cache
        entry = await self.persistent_cache.get(cache_key)
        if entry and isinstance(entry.data, MarketData):
            logger.debug(f"Persistent cache hit for {location}")
            
            # Promote to memory cache if high quality
            if entry.quality_score > 0.7:
                await self.memory_cache.set(cache_key, entry)
            
            return entry.data
        
        logger.debug(f"Cache miss for {location}")
        return None
    
    async def update_cache(self, location: str, data: MarketData) -> None:
        """Update cache with new market data"""
        cache_key = self._generate_cache_key(location)
        
        # Calculate data quality score
        quality_score = self._calculate_quality_score(data)
        
        # Create cache entry
        now = datetime.now()
        expiry_time = now + timedelta(hours=self.default_ttl_hours)
        
        # Estimate size (rough approximation)
        data_size = len(json.dumps(asdict(data), default=str))
        
        entry = CacheEntry(
            key=cache_key,
            data=data,
            created_at=now,
            last_accessed=now,
            access_count=1,
            expiry_time=expiry_time,
            size_bytes=data_size,
            source=','.join(data.data_sources),
            quality_score=quality_score
        )
        
        # Store in both caches
        await self.memory_cache.set(cache_key, entry)
        await self.persistent_cache.set(cache_key, entry)
        
        logger.debug(f"Updated cache for {location} with quality score {quality_score:.2f}")
    
    def _generate_cache_key(self, location: str) -> str:
        """Generate normalized cache key for better hit rates"""
        import re
        
        # Normalize location string for better cache matching
        normalized = location.lower().strip()
        
        # Remove common punctuation and extra spaces
        normalized = re.sub(r'[^\w\s,]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Standardize state representations
        state_mappings = {
            'new york': 'ny', 'california': 'ca', 'texas': 'tx', 'florida': 'fl',
            'illinois': 'il', 'pennsylvania': 'pa', 'ohio': 'oh', 'georgia': 'ga',
            'north carolina': 'nc', 'michigan': 'mi', 'new jersey': 'nj', 'virginia': 'va',
            'washington': 'wa', 'arizona': 'az', 'massachusetts': 'ma', 'tennessee': 'tn',
            'colorado': 'co', 'minnesota': 'mn', 'oregon': 'or'
        }
        
        # Apply state mappings
        for full_name, abbrev in state_mappings.items():
            normalized = normalized.replace(full_name, abbrev)
        
        # Standardize city name variations
        city_mappings = {
            'new york city': 'new york', 'nyc': 'new york',
            'la': 'los angeles', 'san fran': 'san francisco', 'sf': 'san francisco',
            'vegas': 'las vegas', 'philly': 'philadelphia'
        }
        
        for variation, standard in city_mappings.items():
            if variation in normalized:
                normalized = normalized.replace(variation, standard)
        
        # Ensure consistent format: "city, state"
        parts = normalized.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip()
            normalized = f"{city}, {state}"
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _calculate_quality_score(self, data: MarketData) -> float:
        """Calculate data quality score based on freshness and confidence"""
        base_score = data.confidence_score
        
        # Adjust for freshness
        if data.freshness_hours <= 6:
            freshness_multiplier = 1.0
        elif data.freshness_hours <= 24:
            freshness_multiplier = 0.9
        elif data.freshness_hours <= 72:
            freshness_multiplier = 0.7
        else:
            freshness_multiplier = 0.5
        
        # Adjust for data completeness
        completeness_score = 1.0
        if data.median_rent_per_sqm <= 0:
            completeness_score *= 0.8
        if data.median_property_price <= 0:
            completeness_score *= 0.8
        if not data.current_mortgage_rates:
            completeness_score *= 0.9
        
        return min(1.0, base_score * freshness_multiplier * completeness_score)
    
    async def get_performance_stats(self) -> CacheStats:
        """Get comprehensive cache performance statistics"""
        memory_stats = await self.memory_cache.get_stats()
        persistent_stats = await self.persistent_cache.get_stats()
        
        # Combine statistics
        total_hit_count = memory_stats['hit_count'] + persistent_stats['hit_count']
        total_miss_count = memory_stats['miss_count'] + persistent_stats['miss_count']
        total_requests = total_hit_count + total_miss_count
        
        hit_rate = total_hit_count / total_requests if total_requests > 0 else 0.0
        
        # Weighted average response time
        memory_weight = memory_stats['hit_count'] / total_hit_count if total_hit_count > 0 else 0
        persistent_weight = persistent_stats['hit_count'] / total_hit_count if total_hit_count > 0 else 0
        
        avg_response_time = (
            memory_stats['avg_response_time_ms'] * memory_weight +
            persistent_stats['avg_response_time_ms'] * persistent_weight
        )
        
        return CacheStats(
            hit_count=total_hit_count,
            miss_count=total_miss_count,
            total_requests=total_requests,
            hit_rate=hit_rate,
            avg_response_time_ms=avg_response_time,
            cache_size_mb=memory_stats['cache_size_mb'] + persistent_stats['cache_size_mb'],
            entry_count=memory_stats['entry_count'] + persistent_stats['entry_count'],
            oldest_entry=min(filter(None, [memory_stats.get('oldest_entry'), 
                                         persistent_stats.get('oldest_entry')]), default=None),
            newest_entry=max(filter(None, [memory_stats.get('newest_entry'), 
                                         persistent_stats.get('newest_entry')]), default=None)
        )
    
    async def cleanup_expired_entries(self) -> Dict[str, int]:
        """Remove expired entries from all caches"""
        # Memory cache cleanup (automatic via LRU)
        memory_cleaned = 0
        
        # Persistent cache cleanup
        persistent_cleaned = await self.persistent_cache.cleanup_expired()
        
        # Remove very old entries
        cutoff_time = datetime.now() - timedelta(days=self.max_cache_age_days)
        
        self.last_cleanup_time = datetime.now()
        
        logger.info(f"Cache cleanup completed: {persistent_cleaned} expired entries removed")
        
        return {
            'memory_cache_cleaned': memory_cleaned,
            'persistent_cache_cleaned': persistent_cleaned,
            'cleanup_timestamp': self.last_cleanup_time.isoformat()
        }
    
    async def optimize_cache_performance(self) -> Dict[str, Any]:
        """Analyze and optimize cache performance"""
        stats = await self.get_performance_stats()
        
        recommendations = []
        adjustments_made = []
        
        # Check hit rate
        if stats.hit_rate < self.target_hit_rate:
            recommendations.append(
                f"Cache hit rate ({stats.hit_rate:.2%}) is below target ({self.target_hit_rate:.2%}). "
                f"Consider increasing cache size or TTL."
            )
        
        # Check response time
        if stats.avg_response_time_ms > self.target_response_time_ms:
            recommendations.append(
                f"Average response time ({stats.avg_response_time_ms:.1f}ms) is above target "
                f"({self.target_response_time_ms:.1f}ms). Consider optimizing cache backends."
            )
        
        # Auto-adjustments
        if stats.hit_rate > 0.95 and stats.cache_size_mb > 100:
            # Very high hit rate with large cache - might be over-caching
            recommendations.append("Consider reducing cache TTL to free up memory")
        
        optimization_result = {
            'timestamp': datetime.now().isoformat(),
            'current_performance': asdict(stats),
            'recommendations': recommendations,
            'adjustments_made': adjustments_made,
            'meets_target_hit_rate': stats.hit_rate >= self.target_hit_rate,
            'meets_target_response_time': stats.avg_response_time_ms <= self.target_response_time_ms
        }
        
        self.performance_history.append(optimization_result)
        
        # Keep only last 24 hours of history
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.performance_history = [
            h for h in self.performance_history 
            if datetime.fromisoformat(h['timestamp']) > cutoff_time
        ]
        
        return optimization_result
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop_background_tasks(self):
        """Stop background maintenance tasks"""
        for task in [self._cleanup_task, self._monitor_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    async def _cleanup_loop(self):
        """Background task for periodic cache cleanup"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.cleanup_expired_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
    
    async def _monitor_loop(self):
        """Background task for performance monitoring"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                await self.optimize_cache_performance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache monitor loop: {e}")
    
    async def close(self):
        """Clean shutdown of cache manager"""
        await self.stop_background_tasks()
        # Backends will be cleaned up by their destructors


def create_cache_manager(config: Optional[Dict] = None) -> IntelligentCacheManager:
    """Factory function to create IntelligentCacheManager instance"""
    return IntelligentCacheManager(config)