import json
import os
import time
from typing import Dict, Any, Optional, Union
import pickle

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class CacheManager:
    """Manager for caching detection results."""
    
    def __init__(self, cache_dir: str = 'cache', 
                redis_url: Optional[str] = None,
                ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for local file cache
            redis_url: Redis connection URL (e.g. redis://localhost:6379/0)
            ttl: Time-to-live for cache entries in seconds
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.redis_url = redis_url
        self.redis_client = None
        
        # Initialize cache directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # Initialize Redis if URL provided and library available
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Warning: Failed to connect to Redis: {e}")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for the given key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found or expired
        """
        # Try Redis first if available
        if self.redis_client:
            data = self.redis_client.get(f"graphextractor:{key}")
            if data:
                return pickle.loads(data)
        
        # Fall back to file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if os.path.exists(cache_file):
            # Check if file is not expired
            mod_time = os.path.getmtime(cache_file)
            if time.time() - mod_time < self.ttl:
                with open(cache_file, 'r') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        # Invalid cache file
                        os.remove(cache_file)
            else:
                # Expired cache file
                os.remove(cache_file)
                
        return None
    
    def set(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Store result in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            
        Returns:
            Success status
        """
        # Try Redis first if available
        if self.redis_client:
            try:
                pickled_data = pickle.dumps(data)
                return self.redis_client.setex(
                    f"graphextractor:{key}", 
                    self.ttl,
                    pickled_data
                )
            except Exception as e:
                print(f"Warning: Failed to store in Redis: {e}")
        
        # Fall back to file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Failed to write cache file: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Success status
        """
        success = True
        
        # Remove from Redis if available
        if self.redis_client:
            try:
                self.redis_client.delete(f"graphextractor:{key}")
            except Exception:
                success = False
        
        # Remove file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception:
                success = False
                
        return success
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            Success status
        """
        success = True
        
        # Clear Redis cache if available
        if self.redis_client:
            try:
                self.redis_client.delete(self.redis_client.keys("graphextractor:*") or [])
            except Exception:
                success = False
        
        # Clear file cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except Exception:
                    success = False
                    
        return success
