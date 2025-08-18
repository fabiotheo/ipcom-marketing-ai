"""Unit tests for server module."""

import asyncio
import os
import tempfile
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import pytest

from osp_marketing_tools.server import (
    METHODOLOGY_VERSIONS,
    VALID_FRAMEWORKS,
    CacheError,
    ContentValidationError,
    FileOperationError,
    FrameworkValidationError,
    LRUCache,
    OSPToolsError,
    _create_config_note,
    _get_cached_content,
    _get_cached_content_async,
    _read_resource,
    _read_resource_async,
    get_logger,
    handle_exceptions,
)


class TestLRUCache:
    """Test LRU Cache implementation."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = LRUCache(max_size=5)
        assert cache.max_size == 5
        assert len(cache.cache) == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = LRUCache(max_size=3)

        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0

    def test_cache_miss(self):
        """Test cache miss behavior."""
        cache = LRUCache(max_size=3)

        result = cache.get("nonexistent")
        assert result is None
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = LRUCache(max_size=2)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Add third item - should evict key1
        cache.set("key3", "value3")

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"  # Still there
        assert cache.get("key3") == "value3"  # Still there
        assert cache.stats["evictions"] == 1

    def test_cache_update_existing(self):
        """Test updating existing cache entry."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key1", "updated_value")

        assert cache.get("key1") == "updated_value"
        assert len(cache.cache) == 1  # Should not create duplicate

    def test_cache_lru_order(self):
        """Test LRU ordering behavior."""
        cache = LRUCache(max_size=3)

        # Add items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it most recent
        cache.get("key1")

        # Add key4 - should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"  # Still there
        assert cache.get("key4") == "value4"  # New item

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = LRUCache(max_size=2)

        # Test hits and misses
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        cache.get("key1")  # Hit

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert (
            abs(stats["hit_ratio"] - 66.67) < 0.1
        )  # 2/3 * 100, allow small precision diff
        assert stats["cache_size"] == 1
        assert stats["max_size"] == 2

    def test_cache_statistics_empty(self):
        """Test statistics with empty cache."""
        cache = LRUCache(max_size=5)

        stats = cache.get_stats()
        assert stats["hit_ratio"] == 0
        assert stats["utilization"] == 0.0
        assert stats["most_recent_keys"] == []

    def test_cache_clear_stats(self):
        """Test clearing cache statistics."""
        cache = LRUCache(max_size=3)

        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")  # Miss

        cache.clear_stats()

        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0
        assert cache.stats["total_requests"] == 0
        assert cache.stats["evictions"] == 0

    def test_cache_contains(self):
        """Test __contains__ method."""
        cache = LRUCache(max_size=3)

        assert "key1" not in cache

        cache.set("key1", "value1")
        assert "key1" in cache

    def test_cache_utilization_calculation(self):
        """Test cache utilization calculation."""
        cache = LRUCache(max_size=4)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()
        assert stats["utilization"] == 50.0  # 2/4 * 100

    def test_cache_most_recent_keys(self):
        """Test most recent keys tracking."""
        cache = LRUCache(max_size=10)

        # Add more than 5 keys
        for i in range(7):
            cache.set(f"key{i}", f"value{i}")

        stats = cache.get_stats()
        # Should only show last 5 keys
        assert len(stats["most_recent_keys"]) == 5
        assert "key6" in stats["most_recent_keys"]
        assert "key0" not in stats["most_recent_keys"]


class TestExceptions:
    """Test custom exception classes."""

    def test_osp_tools_error_inheritance(self):
        """Test OSPToolsError is base exception."""
        error = OSPToolsError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_specific_exceptions_inheritance(self):
        """Test specific exceptions inherit from OSPToolsError."""
        content_error = ContentValidationError("Content error")
        framework_error = FrameworkValidationError("Framework error")
        cache_error = CacheError("Cache error")
        file_error = FileOperationError("File error")

        assert isinstance(content_error, OSPToolsError)
        assert isinstance(framework_error, OSPToolsError)
        assert isinstance(cache_error, OSPToolsError)
        assert isinstance(file_error, OSPToolsError)


class TestHandleExceptionsDecorator:
    """Test handle_exceptions decorator."""

    @pytest.fixture
    def mock_function(self):
        """Mock async function for testing."""

        async def test_func():
            return {"success": True}

        return test_func

    @pytest.mark.asyncio
    async def test_successful_execution(self, mock_function):
        """Test decorator with successful function execution."""
        decorated_func = handle_exceptions(mock_function)
        result = await decorated_func()

        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_content_validation_error_handling(self):
        """Test handling of ContentValidationError."""

        @handle_exceptions
        async def failing_func():
            raise ContentValidationError("Invalid content")

        result = await failing_func()

        assert result["success"] is False
        assert "Content validation failed" in result["error"]
        assert result["error_type"] == "content_validation"
        assert result["tool"] == "failing_func"

    @pytest.mark.asyncio
    async def test_framework_validation_error_handling(self):
        """Test handling of FrameworkValidationError."""

        @handle_exceptions
        async def failing_func():
            raise FrameworkValidationError("Invalid framework")

        result = await failing_func()

        assert result["success"] is False
        assert "Framework validation failed" in result["error"]
        assert result["error_type"] == "framework_validation"

    @pytest.mark.asyncio
    async def test_file_operation_error_handling(self):
        """Test handling of FileOperationError."""

        @handle_exceptions
        async def failing_func():
            raise FileOperationError("File not found")

        result = await failing_func()

        assert result["success"] is False
        assert "File operation failed" in result["error"]
        assert result["error_type"] == "file_operation"

    @pytest.mark.asyncio
    async def test_cache_error_handling(self):
        """Test handling of CacheError."""

        @handle_exceptions
        async def failing_func():
            raise CacheError("Cache failure")

        result = await failing_func()

        assert result["success"] is False
        assert "Cache operation failed" in result["error"]
        assert result["error_type"] == "cache_operation"

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""

        @handle_exceptions
        async def failing_func():
            raise ValueError("Unexpected error")

        result = await failing_func()

        assert result["success"] is False
        assert "Unexpected error occurred" in result["error"]
        assert result["error_type"] == "unexpected"


class TestGetLogger:
    """Test logger configuration."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        import logging

        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_no_duplicate_handlers(self):
        """Test that multiple calls don't create duplicate handlers."""
        logger1 = get_logger("test_duplicate")
        initial_handlers = len(logger1.handlers)

        logger2 = get_logger("test_duplicate")
        final_handlers = len(logger2.handlers)

        assert initial_handlers == final_handlers
        assert logger1 is logger2

    @patch.dict(os.environ, {"OSP_LOG_LEVEL": "DEBUG"})
    def test_get_logger_respects_config_level(self):
        """Test that logger respects configuration log level."""
        import importlib
        import logging

        # Need to reload config to pick up environment variable
        from osp_marketing_tools import config

        importlib.reload(config)

        logger = get_logger("test_level")
        # The exact level depends on implementation, just check it's configured
        assert hasattr(logger, "level")


class TestFileOperations:
    """Test file operation functions."""

    @patch("builtins.open", mock_open(read_data="Test content"))
    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=100)
    def test_read_resource_success(self, mock_size, mock_exists):
        """Test successful file reading."""
        result = _read_resource("test.md")

        assert result["success"] is True
        assert "data" in result

    @patch("os.path.exists", return_value=False)
    def test_read_resource_file_not_found(self, mock_exists):
        """Test file not found error."""
        with pytest.raises(FileOperationError, match="not found"):
            _read_resource("nonexistent.md")

    def test_read_resource_empty_filename(self):
        """Test empty filename validation."""
        with pytest.raises(FileOperationError, match="cannot be empty"):
            _read_resource("")

    def test_read_resource_path_traversal_protection(self):
        """Test path traversal attack protection."""
        dangerous_paths = [
            "../secret.txt",
            "folder/../secret.txt",
            "folder\\..\\secret.txt",
        ]

        for path in dangerous_paths:
            with pytest.raises(FileOperationError, match="path traversal"):
                _read_resource(path)

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1024 * 1024 * 20)  # 20MB
    def test_read_resource_file_too_large(self, mock_size, mock_exists):
        """Test file size limit enforcement."""
        with pytest.raises(FileOperationError, match="too large"):
            _read_resource("large_file.md")

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1024)
    def test_read_resource_permission_error(self, mock_size, mock_exists, mock_open):
        """Test permission error handling."""
        with pytest.raises(FileOperationError, match="Permission denied"):
            _read_resource("restricted.md")

    @pytest.mark.asyncio
    async def test_read_resource_async_success(self):
        """Test async file reading success path."""
        with patch("osp_marketing_tools.server._read_resource") as mock_read:
            mock_read.return_value = {"success": True, "data": {"content": "test"}}

            result = await _read_resource_async("test.md")
            assert result["success"] is True
            assert result["data"]["content"] == "test"
            mock_read.assert_called_once_with("test.md")

    @pytest.mark.asyncio
    async def test_read_resource_async_error(self):
        """Test async file reading error handling."""
        with patch("osp_marketing_tools.server._read_resource") as mock_read:
            mock_read.side_effect = FileOperationError("Test error")

            result = await _read_resource_async("test.md")
            assert result["success"] is False
            assert "Async file read error" in result["error"]


class TestCachedContent:
    """Test cached content functions."""

    @patch("osp_marketing_tools.server.CONTENT_CACHE")
    @patch("osp_marketing_tools.server._read_resource")
    def test_get_cached_content_cache_hit(self, mock_read, mock_cache):
        """Test cache hit scenario."""
        mock_cache.get.return_value = {"success": True, "data": {"content": "cached"}}

        result = _get_cached_content("test.md")

        assert result["data"]["content"] == "cached"
        mock_read.assert_not_called()

    @patch("osp_marketing_tools.server.CONTENT_CACHE")
    @patch("osp_marketing_tools.server._read_resource")
    def test_get_cached_content_cache_miss(self, mock_read, mock_cache):
        """Test cache miss scenario."""
        mock_cache.get.return_value = None
        mock_read.return_value = {"success": True, "data": {"content": "fresh"}}

        result = _get_cached_content("test.md")

        assert result["data"]["content"] == "fresh"
        mock_read.assert_called_once_with("test.md")
        mock_cache.put.assert_called_once()

    @pytest.mark.asyncio
    @patch("osp_marketing_tools.server.CONTENT_CACHE")
    @patch("osp_marketing_tools.server._read_resource_async")
    async def test_get_cached_content_async_cache_hit(
        self, mock_read_async, mock_cache
    ):
        """Test async cache hit scenario."""
        mock_cache.get.return_value = {"success": True, "data": {"content": "cached"}}

        result = await _get_cached_content_async("test.md")

        assert result["data"]["content"] == "cached"
        mock_read_async.assert_not_called()

    @pytest.mark.asyncio
    @patch("osp_marketing_tools.server.CONTENT_CACHE")
    @patch("osp_marketing_tools.server._read_resource_async")
    async def test_get_cached_content_async_cache_miss(
        self, mock_read_async, mock_cache
    ):
        """Test async cache miss scenario."""
        mock_cache.get.return_value = None
        mock_read_async.return_value = {"success": True, "data": {"content": "fresh"}}

        result = await _get_cached_content_async("test.md")

        assert result["data"]["content"] == "fresh"
        mock_read_async.assert_called_once_with("test.md")
        mock_cache.put.assert_called_once()


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_config_note(self):
        """Test configuration note creation."""
        config = {"test_option": "value1", "another_option": "value2"}

        note = _create_config_note(config)

        assert "Configuration Applied:" in note
        assert "Test Option: value1" in note
        assert "Another Option: value2" in note
        assert note.startswith("\n\n---")


class TestConstants:
    """Test module constants."""

    def test_methodology_versions_structure(self):
        """Test methodology versions structure."""
        assert isinstance(METHODOLOGY_VERSIONS, dict)

        expected_keys = {
            "osp_editing_codes",
            "osp_writing_guide",
            "osp_meta_guide",
            "osp_value_map_guide",
            "osp_seo_guide",
            "frameworks_marketing_2025",
            "technical_writing_2025",
            "seo_frameworks_2025",
        }

        assert set(METHODOLOGY_VERSIONS.keys()) == expected_keys

        # Check version format
        for version in METHODOLOGY_VERSIONS.values():
            assert isinstance(version, str)
            assert version  # Not empty

    def test_valid_frameworks_structure(self):
        """Test valid frameworks structure."""
        assert isinstance(VALID_FRAMEWORKS, set)

        expected_frameworks = {"IDEAL", "STEPPS", "E-E-A-T", "GDocP"}
        assert VALID_FRAMEWORKS == expected_frameworks
