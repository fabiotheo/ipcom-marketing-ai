"""Unit tests for config module."""

import os
from unittest.mock import patch

import pytest

from osp_marketing_tools.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_values(self, clean_environment):
        """Test that default configuration values are set correctly."""
        # Reload the config module to ensure clean state
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        # Test default values
        assert config.Config.CACHE_MAX_SIZE == 50
        assert config.Config.MAX_FILE_SIZE_MB == 10
        assert config.Config.LOG_LEVEL == "INFO"
        assert config.Config.MAX_ANALYSIS_CONTENT_LENGTH == 1000000
        assert config.Config.DEFAULT_ANALYSIS_TIMEOUT_SECONDS == 30
        assert config.Config.ASYNC_EXECUTOR_WORKERS is None
        assert config.Config.HEALTH_CHECK_TIMEOUT_MS == 5000
        assert config.Config.STRICT_FRAMEWORK_VALIDATION is True

    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override default values."""
        # Set environment variables
        monkeypatch.setenv("OSP_CACHE_SIZE", "100")
        monkeypatch.setenv("OSP_MAX_FILE_SIZE_MB", "20")
        monkeypatch.setenv("OSP_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("OSP_MAX_CONTENT_LENGTH", "2000000")
        monkeypatch.setenv("OSP_ANALYSIS_TIMEOUT", "60")
        monkeypatch.setenv("OSP_EXECUTOR_WORKERS", "8")
        monkeypatch.setenv("OSP_HEALTH_TIMEOUT_MS", "10000")
        monkeypatch.setenv("OSP_STRICT_FRAMEWORKS", "false")

        # Reload config to pick up environment variables
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        # Test that environment variables are used
        assert config.Config.CACHE_MAX_SIZE == 100
        assert config.Config.MAX_FILE_SIZE_MB == 20
        assert config.Config.LOG_LEVEL == "DEBUG"
        assert config.Config.MAX_ANALYSIS_CONTENT_LENGTH == 2000000
        assert config.Config.DEFAULT_ANALYSIS_TIMEOUT_SECONDS == 60
        assert config.Config.ASYNC_EXECUTOR_WORKERS == 8
        assert config.Config.HEALTH_CHECK_TIMEOUT_MS == 10000
        assert config.Config.STRICT_FRAMEWORK_VALIDATION is False

    def test_calculated_max_file_size_bytes(self, clean_environment):
        """Test that MAX_FILE_SIZE_BYTES is calculated correctly."""
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        expected_bytes = config.Config.MAX_FILE_SIZE_MB * 1024 * 1024
        assert config.Config.MAX_FILE_SIZE_BYTES == expected_bytes

    def test_boolean_environment_parsing(self, monkeypatch):
        """Test boolean environment variable parsing."""
        # Test various boolean representations
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("False", False),
            ("1", False),  # Only "true" (case insensitive) should be True
            ("0", False),
            ("yes", False),
            ("no", False),
        ]

        for env_value, expected in test_cases:
            monkeypatch.setenv("OSP_STRICT_FRAMEWORKS", env_value)

            import importlib

            from osp_marketing_tools import config

            importlib.reload(config)

            assert (
                config.Config.STRICT_FRAMEWORK_VALIDATION is expected
            ), f"Expected {expected} for '{env_value}'"

    def test_get_env_info(self):
        """Test get_env_info method returns correct structure."""
        env_info = Config.get_env_info()

        # Check that core configuration keys are present
        core_keys = {
            "cache_max_size",
            "max_file_size_mb",
            "log_level",
            "max_content_length",
            "analysis_timeout",
            "executor_workers",
            "health_timeout_ms",
            "strict_framework_validation",
        }

        # Check that v0.3.0 advanced keys are present
        advanced_keys = {
            "cache_ttl_seconds",
            "cache_enable_persistence",
            "batch_max_size",
            "batch_parallel_workers",
            "batch_timeout_seconds",
            "enable_advanced_metrics",
            "enable_content_preprocessing",
            "enable_rate_limiting",
            "rate_limit_requests_per_minute",
            "enterprise_mode",
            "audit_logging",
            "default_tool_profile",
        }

        all_expected_keys = core_keys | advanced_keys
        assert set(env_info.keys()) == all_expected_keys

        # Check types
        assert isinstance(env_info["cache_max_size"], int)
        assert isinstance(env_info["max_file_size_mb"], int)
        assert isinstance(env_info["log_level"], str)
        assert isinstance(env_info["max_content_length"], int)
        assert isinstance(env_info["analysis_timeout"], int)
        assert isinstance(env_info["health_timeout_ms"], int)
        assert isinstance(env_info["strict_framework_validation"], bool)

        # executor_workers can be int or "auto"
        assert isinstance(env_info["executor_workers"], (int, str))

    def test_validate_config_warnings(self, monkeypatch):
        """Test config validation warnings."""
        # Test small cache size warning
        monkeypatch.setenv("OSP_CACHE_SIZE", "5")
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert any(
            "Cache size" in warning and "very small" in warning for warning in warnings
        )

        # Test large cache size warning
        monkeypatch.setenv("OSP_CACHE_SIZE", "1500")
        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert any(
            "Cache size" in warning and "very large" in warning for warning in warnings
        )

    def test_validate_config_file_size_warnings(self, monkeypatch):
        """Test file size validation warnings."""
        # Test small file size warning
        monkeypatch.setenv("OSP_MAX_FILE_SIZE_MB", "0")
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert any(
            "File size limit" in warning and "very small" in warning
            for warning in warnings
        )

        # Test large file size warning
        monkeypatch.setenv("OSP_MAX_FILE_SIZE_MB", "150")
        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert any(
            "File size limit" in warning and "very large" in warning
            for warning in warnings
        )

    def test_validate_config_timeout_warnings(self, monkeypatch):
        """Test timeout validation warnings."""
        monkeypatch.setenv("OSP_ANALYSIS_TIMEOUT", "2")
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert any(
            "Analysis timeout" in warning and "too short" in warning
            for warning in warnings
        )

    def test_validate_config_no_warnings(self, monkeypatch):
        """Test that reasonable config values produce no warnings."""
        monkeypatch.setenv("OSP_CACHE_SIZE", "50")
        monkeypatch.setenv("OSP_MAX_FILE_SIZE_MB", "10")
        monkeypatch.setenv("OSP_ANALYSIS_TIMEOUT", "30")

        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        warnings = config.Config.validate_config()
        assert warnings == []

    def test_integer_parsing_edge_cases(self, monkeypatch):
        """Test edge cases in integer environment variable parsing."""
        # Test non-numeric values (should use defaults)
        monkeypatch.setenv("OSP_CACHE_SIZE", "not_a_number")

        # This should raise ValueError when trying to convert
        with pytest.raises(ValueError):
            import importlib

            from osp_marketing_tools import config

            importlib.reload(config)

    def test_executor_workers_none_handling(self, clean_environment):
        """Test that executor workers defaults to None when not set."""
        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        assert config.Config.ASYNC_EXECUTOR_WORKERS is None

        env_info = config.Config.get_env_info()
        assert env_info["executor_workers"] == "auto"

    def test_executor_workers_with_value(self, monkeypatch):
        """Test executor workers when explicitly set."""
        monkeypatch.setenv("OSP_EXECUTOR_WORKERS", "4")

        import importlib

        from osp_marketing_tools import config

        importlib.reload(config)

        assert config.Config.ASYNC_EXECUTOR_WORKERS == 4

        env_info = config.Config.get_env_info()
        assert env_info["executor_workers"] == 4
