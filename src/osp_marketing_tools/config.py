"""Configuration module for OSP Marketing Tools."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class Config:
    """Configuration management for OSP Marketing Tools."""

    # Cache Configuration
    CACHE_MAX_SIZE: int = int(os.environ.get("OSP_CACHE_SIZE") or "50")

    # File Operation Configuration
    MAX_FILE_SIZE_MB: int = int(os.environ.get("OSP_MAX_FILE_SIZE_MB") or "10")
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    # Logging Configuration
    LOG_LEVEL: str = os.environ.get("OSP_LOG_LEVEL") or "INFO"

    # Analysis Configuration
    MAX_ANALYSIS_CONTENT_LENGTH: int = int(
        os.environ.get("OSP_MAX_CONTENT_LENGTH") or "1000000"
    )  # 1MB default
    DEFAULT_ANALYSIS_TIMEOUT_SECONDS: int = int(
        os.environ.get("OSP_ANALYSIS_TIMEOUT") or "30"
    )

    # Performance Configuration
    ASYNC_EXECUTOR_WORKERS: Optional[int] = (
        None  # None = default (min(32, cpu_count + 4))
    )
    if os.environ.get("OSP_EXECUTOR_WORKERS"):
        ASYNC_EXECUTOR_WORKERS = int(os.environ.get("OSP_EXECUTOR_WORKERS"))

    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT_MS: int = int(os.environ.get("OSP_HEALTH_TIMEOUT_MS", "5000"))

    # Framework Validation Configuration
    STRICT_FRAMEWORK_VALIDATION: bool = (
        os.environ.get("OSP_STRICT_FRAMEWORKS", "true").lower() == "true"
    )

    # Advanced Configuration for v0.3.0
    # Cache Configuration
    CACHE_TTL_SECONDS: int = int(
        os.environ.get("OSP_CACHE_TTL", "3600")
    )  # 1 hour default
    CACHE_ENABLE_PERSISTENCE: bool = (
        os.environ.get("OSP_CACHE_PERSIST", "false").lower() == "true"
    )

    # Batch Processing Configuration
    BATCH_MAX_SIZE: int = int(os.environ.get("OSP_BATCH_MAX_SIZE", "10"))
    BATCH_PARALLEL_WORKERS: int = int(os.environ.get("OSP_BATCH_WORKERS", "4"))
    BATCH_TIMEOUT_SECONDS: int = int(
        os.environ.get("OSP_BATCH_TIMEOUT", "300")
    )  # 5 minutes

    # Analysis Configuration
    ENABLE_ADVANCED_METRICS: bool = (
        os.environ.get("OSP_ADVANCED_METRICS", "true").lower() == "true"
    )
    ENABLE_CONTENT_PREPROCESSING: bool = (
        os.environ.get("OSP_CONTENT_PREPROCESSING", "true").lower() == "true"
    )

    # Security Configuration
    ENABLE_RATE_LIMITING: bool = (
        os.environ.get("OSP_RATE_LIMITING", "false").lower() == "true"
    )
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.environ.get("OSP_RATE_LIMIT", "60"))

    # Enterprise Configuration
    ENTERPRISE_MODE: bool = (
        os.environ.get("OSP_ENTERPRISE_MODE", "false").lower() == "true"
    )
    AUDIT_LOGGING: bool = os.environ.get("OSP_AUDIT_LOGGING", "false").lower() == "true"

    # Tool-specific Configuration (simplified)
    DEFAULT_TOOL_PROFILE: str = os.environ.get("OSP_TOOL_PROFILE", "standard")

    @classmethod
    def get_env_info(cls) -> dict:
        """Get environment configuration information."""
        return {
            # Core Configuration
            "cache_max_size": cls.CACHE_MAX_SIZE,
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "log_level": cls.LOG_LEVEL,
            "max_content_length": cls.MAX_ANALYSIS_CONTENT_LENGTH,
            "analysis_timeout": cls.DEFAULT_ANALYSIS_TIMEOUT_SECONDS,
            "executor_workers": cls.ASYNC_EXECUTOR_WORKERS or "auto",
            "health_timeout_ms": cls.HEALTH_CHECK_TIMEOUT_MS,
            "strict_framework_validation": cls.STRICT_FRAMEWORK_VALIDATION,
            # Advanced Configuration v0.3.0
            "cache_ttl_seconds": cls.CACHE_TTL_SECONDS,
            "cache_enable_persistence": cls.CACHE_ENABLE_PERSISTENCE,
            "batch_max_size": cls.BATCH_MAX_SIZE,
            "batch_parallel_workers": cls.BATCH_PARALLEL_WORKERS,
            "batch_timeout_seconds": cls.BATCH_TIMEOUT_SECONDS,
            "enable_advanced_metrics": cls.ENABLE_ADVANCED_METRICS,
            "enable_content_preprocessing": cls.ENABLE_CONTENT_PREPROCESSING,
            "enable_rate_limiting": cls.ENABLE_RATE_LIMITING,
            "rate_limit_requests_per_minute": cls.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "enterprise_mode": cls.ENTERPRISE_MODE,
            "audit_logging": cls.AUDIT_LOGGING,
            "default_tool_profile": cls.DEFAULT_TOOL_PROFILE,
        }

    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate configuration values and return any warnings."""
        warnings = []

        if cls.CACHE_MAX_SIZE < 10:
            warnings.append(
                f"Cache size ({cls.CACHE_MAX_SIZE}) is very small, consider increasing"
            )
        elif cls.CACHE_MAX_SIZE > 1000:
            warnings.append(
                f"Cache size ({cls.CACHE_MAX_SIZE}) is very large, consider reducing"
            )

        if cls.MAX_FILE_SIZE_MB < 1:
            warnings.append(f"File size limit ({cls.MAX_FILE_SIZE_MB}MB) is very small")
        elif cls.MAX_FILE_SIZE_MB > 100:
            warnings.append(f"File size limit ({cls.MAX_FILE_SIZE_MB}MB) is very large")

        if cls.DEFAULT_ANALYSIS_TIMEOUT_SECONDS < 5:
            warnings.append(
                f"Analysis timeout ({cls.DEFAULT_ANALYSIS_TIMEOUT_SECONDS}s) may be too short"
            )

        # New validations for v0.3.0
        if cls.CACHE_TTL_SECONDS < 60:
            warnings.append(f"Cache TTL ({cls.CACHE_TTL_SECONDS}s) is very short")
        elif cls.CACHE_TTL_SECONDS > 86400:  # 24 hours
            warnings.append(f"Cache TTL ({cls.CACHE_TTL_SECONDS}s) is very long")

        if cls.BATCH_MAX_SIZE < 1:
            warnings.append("Batch max size cannot be less than 1")
        elif cls.BATCH_MAX_SIZE > 100:
            warnings.append(f"Batch max size ({cls.BATCH_MAX_SIZE}) is very large")

        if cls.BATCH_PARALLEL_WORKERS < 1:
            warnings.append("Batch parallel workers cannot be less than 1")
        elif cls.BATCH_PARALLEL_WORKERS > 32:
            warnings.append(
                f"Batch parallel workers ({cls.BATCH_PARALLEL_WORKERS}) may be excessive"
            )

        if cls.ENABLE_RATE_LIMITING and cls.RATE_LIMIT_REQUESTS_PER_MINUTE < 1:
            warnings.append("Rate limit cannot be less than 1 request per minute")

        return warnings


# NOTE: ToolParameterProfile removed as it was not being used by MCP tools
# MCP tools accept parameters directly instead of using profiles
# If needed in the future, can be re-implemented based on actual usage patterns


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing operations."""

    max_batch_size: int = 10
    parallel_workers: int = 4
    timeout_seconds: int = 300
    enable_progress_tracking: bool = True
    enable_error_aggregation: bool = True
    retry_failed_items: bool = True
    max_retries: int = 3


@dataclass
class CacheConfig:
    """Advanced cache configuration."""

    max_size: int = 50
    ttl_seconds: int = 3600
    enable_persistence: bool = False
    persistence_path: Optional[str] = None
    enable_compression: bool = True
    enable_metrics: bool = True


class ConfigManager:
    """Simplified configuration management for v0.3.0."""

    def __init__(self):
        # Removed complex profile system as it wasn't being used
        # MCP tools accept parameters directly
        pass

    def get_batch_config(self) -> BatchProcessingConfig:
        """Get batch processing configuration."""
        return BatchProcessingConfig(
            max_batch_size=Config.BATCH_MAX_SIZE,
            parallel_workers=Config.BATCH_PARALLEL_WORKERS,
            timeout_seconds=Config.BATCH_TIMEOUT_SECONDS,
        )

    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return CacheConfig(
            max_size=Config.CACHE_MAX_SIZE,
            ttl_seconds=Config.CACHE_TTL_SECONDS,
            enable_persistence=Config.CACHE_ENABLE_PERSISTENCE,
        )

    def load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_config_file(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save configuration to JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)


# Global configuration manager instance
config_manager = ConfigManager()
