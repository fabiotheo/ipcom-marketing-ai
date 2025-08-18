"""Unit tests for advanced caching system."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from osp_marketing_tools.cache import (AdvancedLRUCache, CacheEntry,
                                       CacheManager, LRUCache, cache_manager)


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=1234567890.0,
            accessed_at=1234567890.0,
            access_count=5,
            tags=["tag1", "tag2"],
        )

        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.created_at == 1234567890.0
        assert entry.accessed_at == 1234567890.0
        assert entry.access_count == 5
        assert entry.tags == ["tag1", "tag2"]
        assert entry.size_bytes > 0

    def test_cache_entry_defaults(self):
        """Test CacheEntry with default values."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=1234567890.0,
            accessed_at=1234567890.0,
        )

        assert entry.access_count == 0
        assert entry.tags == []
        assert entry.size_bytes > 0

    def test_cache_entry_size_calculation(self):
        """Test automatic size calculation."""
        entry = CacheEntry(
            key="key",
            value="a" * 100,  # 100 character string
            created_at=time.time(),
            accessed_at=time.time(),
        )

        assert entry.size_bytes >= 100

    def test_is_expired(self):
        """Test expiration checking."""
        current_time = time.time()

        # Not expired
        entry = CacheEntry(
            key="key", value="value", created_at=current_time, accessed_at=current_time
        )
        assert not entry.is_expired(3600)  # 1 hour TTL

        # Expired
        old_entry = CacheEntry(
            key="key",
            value="value",
            created_at=current_time - 7200,  # 2 hours ago
            accessed_at=current_time - 7200,
        )
        assert old_entry.is_expired(3600)  # 1 hour TTL

    def test_touch(self):
        """Test access tracking."""
        entry = CacheEntry(
            key="key",
            value="value",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
        )

        initial_time = entry.accessed_at
        initial_count = entry.access_count

        time.sleep(0.01)  # Small delay
        entry.touch()

        assert entry.accessed_at > initial_time
        assert entry.access_count == initial_count + 1


class TestAdvancedLRUCache:
    """Test AdvancedLRUCache functionality."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        assert cache.max_size == 10
        assert cache.ttl_seconds == 3600
        assert len(cache.cache) == 0

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["current_size"] == 0

    def test_put_and_get_basic(self):
        """Test basic put and get operations."""
        cache = AdvancedLRUCache(max_size=3, ttl_seconds=3600)

        # Put some values
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Get values
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("nonexistent") is None

        # Check stats
        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["current_size"] == 3

    def test_lru_eviction(self):
        """Test LRU eviction when max size is exceeded."""
        cache = AdvancedLRUCache(max_size=2, ttl_seconds=3600)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        stats = cache.get_stats()
        assert stats["evictions"] == 1
        assert stats["current_size"] == 2

    def test_lru_order_update(self):
        """Test that LRU order is updated on access."""
        cache = AdvancedLRUCache(max_size=2, ttl_seconds=3600)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        # Access key1 to make it most recent
        cache.get("key1")

        # Add key3, should evict key2 (least recently used)
        cache.put("key3", "value3")

        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"  # New value

    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=0.1)  # 100ms TTL

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        time.sleep(0.15)  # Wait for expiration

        assert cache.get("key1") is None

        stats = cache.get_stats()
        assert stats["expired_removals"] == 1

    def test_put_with_tags(self):
        """Test putting values with tags."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        cache.put("key1", "value1", tags=["tag1", "tag2"])
        cache.put("key2", "value2", tags=["tag2", "tag3"])
        cache.put("key3", "value3", tags=["tag1"])

        entries = cache.get_entries_info()
        assert len(entries) == 3

        # Check tags are preserved
        entry1 = next(e for e in entries if e["key"] == "key1")
        assert set(entry1["tags"]) == {"tag1", "tag2"}

    def test_invalidate_by_tags(self):
        """Test invalidation by tags."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        cache.put("key1", "value1", tags=["tag1", "tag2"])
        cache.put("key2", "value2", tags=["tag2", "tag3"])
        cache.put("key3", "value3", tags=["tag1"])
        cache.put("key4", "value4", tags=["tag4"])

        # Invalidate by tag1
        removed_count = cache.invalidate_by_tags(["tag1"])
        assert removed_count == 2  # key1 and key3

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None
        assert cache.get("key4") == "value4"

    def test_invalidate_single_key(self):
        """Test invalidating a single key."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        assert cache.invalidate("key1") is True
        assert cache.invalidate("nonexistent") is False

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_clear_cache(self):
        """Test clearing all cache entries."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

        stats = cache.get_stats()
        assert stats["current_size"] == 0

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=0.1)  # 100ms TTL

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        time.sleep(0.15)  # Wait for expiration

        # Add a new entry that won't be expired
        cache.put("key3", "value3")

        removed_count = cache.cleanup_expired()
        assert removed_count == 2  # key1 and key2

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_get_entries_info(self):
        """Test getting detailed entry information."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        cache.put("key1", "value1", tags=["tag1"])
        cache.get("key1")  # Access it to update stats

        entries = cache.get_entries_info()
        assert len(entries) == 1

        entry = entries[0]
        assert entry["key"] == "key1"
        assert entry["access_count"] == 1
        assert entry["tags"] == ["tag1"]
        assert entry["age_seconds"] >= 0
        assert entry["is_expired"] is False

    @patch("tempfile.gettempdir")
    def test_persistence_initialization(self, mock_tempdir):
        """Test cache persistence initialization."""
        mock_tempdir.return_value = "/tmp"

        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600, enable_persistence=True)

        assert cache.enable_persistence is True
        assert str(cache.persistence_path).endswith("osp_cache/cache.json")

    def test_persistence_path_from_env(self):
        """Test persistence path from environment variable."""
        with patch.dict(os.environ, {"OSP_CACHE_PATH": "/custom/cache/path"}):
            cache = AdvancedLRUCache(
                max_size=10, ttl_seconds=3600, enable_persistence=True
            )

            assert str(cache.persistence_path) == "/custom/cache/path"

    def test_persistence_path_parameter(self):
        """Test persistence path from parameter."""
        cache = AdvancedLRUCache(
            max_size=10,
            ttl_seconds=3600,
            enable_persistence=True,
            persistence_path="/param/cache/path",
        )

        assert str(cache.persistence_path) == "/param/cache/path"

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    @patch("json.dump")
    def test_save_to_disk_success(
        self, mock_json_dump, mock_mkdir, mock_exists, mock_file
    ):
        """Test successful cache save to disk."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600, enable_persistence=True)

        cache.put("key1", "value1")
        cache._save_to_disk()

        # mkdir might be called multiple times (during init and save)
        assert mock_mkdir.call_count >= 1
        mock_file.assert_called()
        # json.dump might be called multiple times (during put and explicit save)
        assert mock_json_dump.call_count >= 1

    @patch("builtins.open", side_effect=PermissionError("Access denied"))
    @patch("pathlib.Path.mkdir")
    def test_save_to_disk_failure(self, mock_mkdir, mock_file):
        """Test cache save failure handling."""
        with patch("logging.getLogger") as mock_logger:
            cache = AdvancedLRUCache(
                max_size=10, ttl_seconds=3600, enable_persistence=True
            )

            cache.put("key1", "value1")

            # Should not raise exception, just log error
            cache._save_to_disk()

            # Error might be logged multiple times (during put and explicit save)
            assert mock_logger.return_value.error.call_count >= 1

    def test_load_from_disk_success(self):
        """Test successful cache load from disk."""
        current_time = time.time()
        mock_data = {
            "entries": {
                "key1": {
                    "value": "value1",
                    "created_at": current_time,
                    "accessed_at": current_time,
                    "access_count": 0,
                    "tags": [],
                }
            }
        }

        with patch(
            "builtins.open", new_callable=mock_open, read_data=json.dumps(mock_data)
        ):
            with patch("pathlib.Path.exists", return_value=True):
                cache = AdvancedLRUCache(
                    max_size=10,
                    ttl_seconds=86400,  # Long TTL so entries don't expire
                    enable_persistence=True,
                )

                # Should have loaded the entry
                assert cache.get("key1") == "value1"

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_from_disk_failure(self, mock_exists, mock_file):
        """Test cache load failure handling."""
        with patch("logging.getLogger") as mock_logger:
            cache = AdvancedLRUCache(
                max_size=10, ttl_seconds=3600, enable_persistence=True
            )

            # Should not raise exception, just log warning
            mock_logger.return_value.warning.assert_called_once()
            assert len(cache.cache) == 0

    @patch("builtins.open", new_callable=mock_open, read_data='{"invalid": "json"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_from_disk_invalid_format(self, mock_exists, mock_file):
        """Test handling of invalid cache file format."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600, enable_persistence=True)

        # Should start with empty cache
        assert len(cache.cache) == 0

    def test_stats_calculation(self):
        """Test statistics calculation."""
        cache = AdvancedLRUCache(max_size=5, ttl_seconds=3600)

        # Add some entries
        cache.put("key1", "value1")
        cache.put("key2", "value2")

        # Access them
        cache.get("key1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("missing")  # Miss

        stats = cache.get_stats()

        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["hit_ratio"] == 75.0
        assert stats["current_size"] == 2
        assert stats["max_size"] == 5
        assert stats["total_size_bytes"] > 0
        assert stats["avg_access_time_ms"] >= 0


class TestCacheManager:
    """Test CacheManager functionality."""

    def test_manager_initialization(self):
        """Test cache manager initialization."""
        manager = CacheManager()

        assert len(manager.caches) == 0
        assert manager._default_cache is not None

    def test_get_default_cache(self):
        """Test getting default cache."""
        manager = CacheManager()

        cache1 = manager.get_cache()
        cache2 = manager.get_cache("default")

        assert cache1 is cache2
        assert cache1 is manager._default_cache

    def test_get_named_cache(self):
        """Test getting named caches."""
        manager = CacheManager()

        cache1 = manager.get_cache("test_cache")
        cache2 = manager.get_cache("test_cache")
        cache3 = manager.get_cache("other_cache")

        assert cache1 is cache2  # Same instance
        assert cache1 is not cache3  # Different instances
        assert "test_cache" in manager.caches
        assert "other_cache" in manager.caches

    def test_create_cache_with_config(self):
        """Test creating cache with specific configuration."""
        manager = CacheManager()

        cache = manager.create_cache(
            "custom_cache", max_size=5, ttl_seconds=1800, enable_persistence=True
        )

        assert cache.max_size == 5
        assert cache.ttl_seconds == 1800
        assert cache.enable_persistence is True
        assert "custom_cache" in manager.caches

    def test_get_all_stats(self):
        """Test getting statistics for all caches."""
        manager = CacheManager()

        # Add some data to default cache
        manager.get_cache().put("key1", "value1")

        # Create and use named cache
        named_cache = manager.get_cache("test_cache")
        named_cache.put("key2", "value2")

        all_stats = manager.get_all_stats()

        assert "default" in all_stats
        assert "test_cache" in all_stats
        assert all_stats["default"]["current_size"] == 1
        assert all_stats["test_cache"]["current_size"] == 1

    def test_cleanup_all_expired(self):
        """Test cleanup of expired entries across all caches."""
        manager = CacheManager()

        # Setup caches with short TTL
        default_cache = manager.get_cache()
        default_cache.ttl_seconds = 0.1
        default_cache.put("key1", "value1")

        named_cache = manager.create_cache("test_cache", ttl_seconds=0.1)
        named_cache.put("key2", "value2")

        time.sleep(0.15)  # Wait for expiration

        results = manager.cleanup_all_expired()

        assert "default" in results
        assert "test_cache" in results
        assert results["default"] >= 0
        assert results["test_cache"] >= 0

    def test_clear_all_caches(self):
        """Test clearing all caches."""
        manager = CacheManager()

        # Add data to caches
        manager.get_cache().put("key1", "value1")
        manager.get_cache("test_cache").put("key2", "value2")

        manager.clear_all()

        assert manager.get_cache().get("key1") is None
        assert manager.get_cache("test_cache").get("key2") is None


class TestLRUCacheBackwardCompatibility:
    """Test backward compatibility wrapper."""

    def test_legacy_cache_creation(self):
        """Test creating legacy LRUCache."""
        cache = LRUCache(max_size=5)

        assert cache.max_size == 5
        assert cache._cache is not None

    def test_legacy_set_get_methods(self):
        """Test legacy set/get methods."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.put("key2", "value2")  # Both methods should work

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

    def test_legacy_stats_compatibility(self):
        """Test legacy stats format."""
        cache = LRUCache(max_size=5)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")
        cache.get("missing")

        stats = cache.get_stats()

        # Check legacy fields
        assert "utilization" in stats
        assert "total_requests" in stats
        assert "most_recent_keys" in stats
        assert "cache_size" in stats

        assert stats["utilization"] == 40.0  # 2/5 * 100
        assert stats["total_requests"] == 2  # 1 hit + 1 miss
        assert stats["cache_size"] == 2

    def test_legacy_stats_property(self):
        """Test legacy stats property."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")

        stats1 = cache.get_stats()
        stats2 = cache.stats

        assert stats1 == stats2

    def test_legacy_contains_operator(self):
        """Test legacy 'in' operator support."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")

        assert "key1" in cache
        assert "missing" not in cache

    def test_legacy_cache_property(self):
        """Test legacy cache property access."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache_dict = cache.cache

        assert isinstance(cache_dict, dict)
        assert "key1" in cache_dict
        assert "key2" in cache_dict
        assert cache_dict["key1"] == "value1"

    def test_legacy_clear_stats(self):
        """Test legacy clear_stats method."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.get("key1")

        initial_stats = cache.get_stats()
        assert initial_stats["hits"] > 0

        cache.clear_stats()

        new_stats = cache.get_stats()
        assert new_stats["hits"] == 0
        assert new_stats["current_size"] == 0


class TestGlobalCacheManager:
    """Test global cache manager instance."""

    def test_global_manager_exists(self):
        """Test that global manager instance exists."""
        assert cache_manager is not None
        assert isinstance(cache_manager, CacheManager)

    def test_global_manager_is_singleton(self):
        """Test that importing cache_manager gives same instance."""
        from osp_marketing_tools.cache import cache_manager as manager2

        assert cache_manager is manager2

    def test_global_manager_functionality(self):
        """Test basic functionality of global manager."""
        # Clean up any existing state
        cache_manager.clear_all()

        cache = cache_manager.get_cache("test_global")
        cache.put("test_key", "test_value")

        assert cache.get("test_key") == "test_value"

        stats = cache_manager.get_all_stats()
        assert "test_global" in stats


class TestCacheIntegration:
    """Integration tests for cache system."""

    def test_cache_with_complex_objects(self):
        """Test caching complex objects."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        complex_object = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "string": "test",
        }

        cache.put("complex", complex_object)
        retrieved = cache.get("complex")

        assert retrieved == complex_object
        assert retrieved is complex_object  # Same reference

    def test_cache_thread_safety_basics(self):
        """Test basic thread safety considerations."""
        cache = AdvancedLRUCache(max_size=10, ttl_seconds=3600)

        # Test that cache has a lock
        assert cache._lock is not None

        # Test basic operations work with lock
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_performance_under_load(self):
        """Test cache performance under moderate load."""
        cache = AdvancedLRUCache(max_size=100, ttl_seconds=3600)

        start_time = time.time()

        # Add 100 items
        for i in range(100):
            cache.put(f"key_{i}", f"value_{i}")

        # Access all items
        for i in range(100):
            assert cache.get(f"key_{i}") == f"value_{i}"

        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0

        stats = cache.get_stats()
        assert stats["hits"] == 100
        assert stats["current_size"] == 100
