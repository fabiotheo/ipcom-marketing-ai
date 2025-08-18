"""Advanced caching system for OSP Marketing Tools."""

import asyncio
import hashlib
import json
import os
import tempfile
import threading
import time
from collections import OrderedDict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .version import __version__


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    size_bytes: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.size_bytes == 0:
            self.size_bytes = len(str(self.value).encode("utf-8"))

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > ttl_seconds

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = time.time()
        self.access_count += 1


class AdvancedLRUCache:
    """Advanced LRU cache with TTL, persistence, and metrics."""

    def __init__(
        self,
        max_size: int = Config.CACHE_MAX_SIZE,
        ttl_seconds: int = Config.CACHE_TTL_SECONDS,
        enable_persistence: bool = Config.CACHE_ENABLE_PERSISTENCE,
        persistence_path: Optional[str] = None,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_persistence = enable_persistence
        # Use environment variable, passed path, or fall back to temp directory
        if persistence_path:
            self.persistence_path = Path(persistence_path).expanduser()
        elif "OSP_CACHE_PATH" in os.environ:
            self.persistence_path = Path(os.environ["OSP_CACHE_PATH"]).expanduser()
        else:
            # Use system temp directory for better cross-platform compatibility
            temp_dir = Path(tempfile.gettempdir()) / "osp_cache"
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.persistence_path = temp_dir / "cache.json"

        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_removals": 0,
            "total_size_bytes": 0,
            "avg_access_time_ms": 0.0,
        }

        # Load from persistence if enabled
        if self.enable_persistence:
            self._load_from_disk()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL and LRU update."""
        start_time = time.time()

        with self._lock:
            if key not in self.cache:
                self._stats["misses"] += 1
                return None

            entry = self.cache[key]

            # Check if expired
            if entry.is_expired(self.ttl_seconds):
                del self.cache[key]
                self._stats["misses"] += 1
                self._stats["expired_removals"] += 1
                self._update_total_size()
                return None

            # Update LRU order and access stats
            entry.touch()
            self.cache.move_to_end(key)
            self._stats["hits"] += 1

            # Update average access time
            access_time_ms = (time.time() - start_time) * 1000
            total_accesses = self._stats["hits"] + self._stats["misses"]
            self._stats["avg_access_time_ms"] = (
                self._stats["avg_access_time_ms"] * (total_accesses - 1)
                + access_time_ms
            ) / total_accesses

            return entry.value

    def put(self, key: str, value: Any, tags: Optional[List[str]] = None) -> None:
        """Put value in cache with automatic eviction."""
        with self._lock:
            # Remove existing entry if present
            if key in self.cache:
                del self.cache[key]

            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                accessed_at=time.time(),
                tags=tags or [],
            )

            # Add to cache
            self.cache[key] = entry
            self.cache.move_to_end(key)

            # Evict if necessary
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self._stats["evictions"] += 1

            self._update_total_size()

            # Persist if enabled
            if self.enable_persistence:
                self._save_to_disk()

    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                self._update_total_size()
                return True
            return False

    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Remove all entries with any of the given tags."""
        removed_count = 0
        with self._lock:
            keys_to_remove = []
            for key, entry in self.cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]
                removed_count += 1

            self._update_total_size()

        return removed_count

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self._stats["evictions"] += len(self.cache)
            self._update_total_size()

    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        removed_count = 0
        with self._lock:
            keys_to_remove = []
            for key, entry in self.cache.items():
                if entry.is_expired(self.ttl_seconds):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]
                removed_count += 1
                self._stats["expired_removals"] += 1

            self._update_total_size()

        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_ratio = (
                (self._stats["hits"] / total_requests * 100)
                if total_requests > 0
                else 0
            )

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_ratio": round(hit_ratio, 2),
                "evictions": self._stats["evictions"],
                "expired_removals": self._stats["expired_removals"],
                "current_size": len(self.cache),
                "max_size": self.max_size,
                "total_size_bytes": self._stats["total_size_bytes"],
                "avg_access_time_ms": round(self._stats["avg_access_time_ms"], 3),
                "ttl_seconds": self.ttl_seconds,
                "persistence_enabled": self.enable_persistence,
            }

    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Get information about all cache entries."""
        with self._lock:
            entries_info = []
            for entry in self.cache.values():
                entries_info.append(
                    {
                        "key": entry.key,
                        "created_at": entry.created_at,
                        "accessed_at": entry.accessed_at,
                        "access_count": entry.access_count,
                        "size_bytes": entry.size_bytes,
                        "tags": entry.tags,
                        "age_seconds": round(time.time() - entry.created_at, 2),
                        "is_expired": entry.is_expired(self.ttl_seconds),
                    }
                )
            return entries_info

    def _update_total_size(self) -> None:
        """Update total cache size in bytes."""
        self._stats["total_size_bytes"] = sum(
            entry.size_bytes for entry in self.cache.values()
        )

    def _save_to_disk(self) -> None:
        """Save cache to disk for persistence."""
        if not self.enable_persistence:
            return

        try:
            # Create directory if it doesn't exist
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for serialization
            cache_data = {
                "metadata": {
                    "version": __version__,
                    "saved_at": time.time(),
                    "max_size": self.max_size,
                    "ttl_seconds": self.ttl_seconds,
                },
                "entries": {},
            }

            # Serialize cache entries (only non-expired ones)
            for key, entry in self.cache.items():
                if not entry.is_expired(self.ttl_seconds):
                    cache_data["entries"][key] = {
                        "value": entry.value,
                        "created_at": entry.created_at,
                        "accessed_at": entry.accessed_at,
                        "access_count": entry.access_count,
                        "tags": entry.tags,
                    }

            # Write to file
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, default=str)

        except Exception as e:
            # Log persistence failures but don't break cache functionality
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to save cache to disk at {self.persistence_path}: {e}"
            )
            # Cache should still work without persistence

    def _load_from_disk(self) -> None:
        """Load cache from disk if persistence file exists."""
        if not self.enable_persistence or not self.persistence_path.exists():
            return

        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Validate format
            if "entries" not in cache_data:
                return

            # Load entries
            current_time = time.time()
            loaded_count = 0

            for key, entry_data in cache_data["entries"].items():
                # Check if entry would be expired
                created_at = entry_data.get("created_at", current_time)
                if current_time - created_at < self.ttl_seconds:
                    entry = CacheEntry(
                        key=key,
                        value=entry_data["value"],
                        created_at=created_at,
                        accessed_at=entry_data.get("accessed_at", created_at),
                        access_count=entry_data.get("access_count", 0),
                        tags=entry_data.get("tags", []),
                    )
                    self.cache[key] = entry
                    loaded_count += 1

                    if loaded_count >= self.max_size:
                        break

            self._update_total_size()

        except Exception as e:
            # Log loading failures but don't break cache functionality
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Failed to load cache from disk at {self.persistence_path}: {e}"
            )
            # Start with empty cache
            self.cache.clear()


class CacheManager:
    """Global cache manager for different cache types."""

    def __init__(self):
        self.caches: Dict[str, AdvancedLRUCache] = {}
        self._default_cache = AdvancedLRUCache()

    def get_cache(self, cache_name: str = "default") -> AdvancedLRUCache:
        """Get or create a named cache."""
        if cache_name == "default":
            return self._default_cache

        if cache_name not in self.caches:
            self.caches[cache_name] = AdvancedLRUCache()

        return self.caches[cache_name]

    def create_cache(
        self,
        cache_name: str,
        max_size: int = Config.CACHE_MAX_SIZE,
        ttl_seconds: int = Config.CACHE_TTL_SECONDS,
        enable_persistence: bool = Config.CACHE_ENABLE_PERSISTENCE,
    ) -> AdvancedLRUCache:
        """Create a new named cache with specific configuration."""
        cache = AdvancedLRUCache(
            max_size=max_size,
            ttl_seconds=ttl_seconds,
            enable_persistence=enable_persistence,
            persistence_path=os.path.join(
                tempfile.gettempdir(), "osp_cache", f"{cache_name}.json"
            ),
        )
        self.caches[cache_name] = cache
        return cache

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        stats = {"default": self._default_cache.get_stats()}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()
        return stats

    def cleanup_all_expired(self) -> Dict[str, int]:
        """Cleanup expired entries from all caches."""
        results = {"default": self._default_cache.cleanup_expired()}
        for name, cache in self.caches.items():
            results[name] = cache.cleanup_expired()
        return results

    def clear_all(self) -> None:
        """Clear all caches."""
        self._default_cache.clear()
        for cache in self.caches.values():
            cache.clear()


# Global cache manager instance
cache_manager = CacheManager()


# Backward compatibility with existing LRUCache
class LRUCache:
    """Backward compatibility wrapper for AdvancedLRUCache."""

    def __init__(self, max_size: int = Config.CACHE_MAX_SIZE):
        # Create a unique cache instance for each LRUCache instance
        import uuid

        _unique_id = f"legacy_{uuid.uuid4().hex[:8]}"  # noqa: F841
        self._cache = AdvancedLRUCache(
            max_size=max_size,
            ttl_seconds=86400,  # Long TTL for legacy compatibility
            enable_persistence=False,
        )
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Backward compatibility method."""
        self._cache.put(key, value)

    def put(self, key: str, value: Any) -> None:
        self._cache.put(key, value)

    def clear_stats(self) -> None:
        """Clear cache statistics (backward compatibility)."""
        # Reset internal stats by creating a new cache
        self._cache = AdvancedLRUCache(
            max_size=self.max_size, ttl_seconds=86400, enable_persistence=False
        )

    def get_stats(self) -> Dict[str, Any]:
        stats = self._cache.get_stats()
        # Add backward compatibility fields
        utilization = (
            (stats["current_size"] / stats["max_size"]) * 100
            if stats["max_size"] > 0
            else 0
        )
        total_requests = stats["hits"] + stats["misses"]

        # Add missing fields expected by tests
        stats.update(
            {
                "utilization": utilization,
                "total_requests": total_requests,
                "most_recent_keys": (
                    list(self._cache.cache.keys())[-5:] if self._cache.cache else []
                ),
                "cache_size": stats["current_size"],  # Backward compatibility alias
            }
        )
        return stats

    @property
    def stats(self) -> Dict[str, Any]:
        """Backward compatibility property."""
        return self.get_stats()

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator."""
        return self._cache.get(key) is not None

    @property
    def cache(self) -> Dict[str, Any]:
        """Access to internal cache for backward compatibility."""
        return {entry.key: entry.value for entry in self._cache.cache.values()}
