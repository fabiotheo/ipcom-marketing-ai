"""Pytest configuration and shared fixtures for OSP Marketing Tools tests."""

import os
import tempfile
from typing import Any, Dict, Generator
from unittest.mock import Mock, patch

import pytest


# Test data fixtures
@pytest.fixture
def sample_content() -> str:
    """Sample content for testing analysis functions."""
    return """
    This is a comprehensive guide about software development practices.
    We need to identify the target audience and their pain points.
    Our research shows that 85% of developers struggle with deployment.
    Let's implement practical solutions and share best practices.
    Contact us for more information and expert guidance.
    """


@pytest.fixture
def sample_short_content() -> str:
    """Short sample content for edge case testing."""
    return "Short text for testing."


@pytest.fixture
def sample_empty_content() -> str:
    """Empty content for validation testing."""
    return ""


@pytest.fixture
def sample_long_content() -> str:
    """Long content for performance testing."""
    return "This is a test sentence. " * 1000


@pytest.fixture
def sample_frameworks() -> list[str]:
    """Valid framework list for testing."""
    return ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]


@pytest.fixture
def invalid_frameworks() -> list[str]:
    """Invalid framework list for testing."""
    return ["INVALID", "UNKNOWN"]


@pytest.fixture
def mixed_frameworks() -> list[str]:
    """Mixed valid/invalid frameworks for testing."""
    return ["IDEAL", "INVALID", "STEPPS"]


# Configuration fixtures
@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration for testing."""
    return {
        "CACHE_MAX_SIZE": 10,
        "MAX_FILE_SIZE_MB": 1,
        "LOG_LEVEL": "DEBUG",
        "MAX_ANALYSIS_CONTENT_LENGTH": 10000,
        "DEFAULT_ANALYSIS_TIMEOUT_SECONDS": 5,
        "STRICT_FRAMEWORK_VALIDATION": True,
    }


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Temporary file for file operation testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Markdown File\n\nThis is test content.")
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_file_content() -> str:
    """Mock file content for testing."""
    return """
    # OSP Marketing Framework

    This is a comprehensive guide for marketing content creation.
    ## Key Points
    - Audience identification
    - Content strategy
    - Performance measurement
    """


# Cache fixtures
@pytest.fixture
def fresh_cache():
    """Fresh cache instance for isolated testing."""
    from osp_marketing_tools.server import LRUCache

    return LRUCache(max_size=5)


@pytest.fixture
def populated_cache():
    """Cache with some test data."""
    from osp_marketing_tools.server import LRUCache

    cache = LRUCache(max_size=5)
    cache.set("test_key_1", {"data": "test_value_1"})
    cache.set("test_key_2", {"data": "test_value_2"})
    return cache


# Mock fixtures
@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    return Mock()


@pytest.fixture
def mock_async_file_read():
    """Mock async file reading."""

    async def _mock_read(filename: str) -> Dict[str, Any]:
        return {"success": True, "data": {"content": f"Mock content for {filename}"}}

    return _mock_read


# Environment fixtures
@pytest.fixture
def clean_environment(monkeypatch):
    """Clean environment variables for testing."""
    env_vars = [
        "OSP_CACHE_SIZE",
        "OSP_MAX_FILE_SIZE_MB",
        "OSP_LOG_LEVEL",
        "OSP_MAX_CONTENT_LENGTH",
        "OSP_ANALYSIS_TIMEOUT",
        "OSP_EXECUTOR_WORKERS",
        "OSP_HEALTH_TIMEOUT_MS",
        "OSP_STRICT_FRAMEWORKS",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def test_environment(monkeypatch):
    """Set test environment variables."""
    monkeypatch.setenv("OSP_CACHE_SIZE", "5")
    monkeypatch.setenv("OSP_MAX_FILE_SIZE_MB", "1")
    monkeypatch.setenv("OSP_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OSP_STRICT_FRAMEWORKS", "true")


# Analysis fixtures
@pytest.fixture
def expected_analysis_structure() -> Dict[str, Any]:
    """Expected structure for analysis results."""
    return {
        "IDEAL": {
            "identify": {"score": float, "recommendations": str},
            "discover": {"score": float, "recommendations": str},
            "empower": {"score": float, "recommendations": str},
            "activate": {"score": float, "recommendations": str},
            "learn": {"score": float, "recommendations": str},
        }
    }


@pytest.fixture
def benchmark_content() -> str:
    """Content specifically designed for benchmarking."""
    return (
        """
    Expert software development guide for experienced developers.
    We've researched and tested these implementation strategies extensively.
    Our team has successfully applied these methods across 100+ projects.
    Try our recommended approach and share your experience with the community.
    This comprehensive tutorial covers everything from basic setup to advanced optimization.
    Contact our experts for personalized guidance and professional consulting.
    """
        * 10
    )  # Make it longer for performance testing


# Async test helpers
@pytest.fixture
def event_loop():
    """Event loop for async tests."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Performance testing fixtures
@pytest.fixture
def performance_thresholds() -> Dict[str, float]:
    """Performance thresholds for testing."""
    return {
        "cache_hit_time_ms": 1.0,
        "cache_miss_time_ms": 50.0,
        "analysis_time_ms": 100.0,
        "file_read_time_ms": 10.0,
    }
