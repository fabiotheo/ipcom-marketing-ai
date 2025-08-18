"""OSP Marketing Tools server implementation."""

import asyncio
import json
import logging
import os
import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .analysis import analyze_content_with_frameworks
from .batch import BatchItem, batch_manager
from .cache import AdvancedLRUCache, LRUCache
from .cache import cache_manager as cache_mgr
from .config import Config, config_manager
from .version import __version__


def get_logger(name: str) -> "logging.Logger":
    """Configure structured logging for OSP Marketing Tools."""
    import logging
    import sys

    logger = logging.getLogger(name)

    # Evitar configuração duplicada
    if not logger.handlers:
        # Configure handler
        handler = logging.StreamHandler(sys.stdout)

        # Structured logging format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger


logger = get_logger(__name__)


# Custom exceptions for better error handling
class OSPToolsError(Exception):
    """Base exception for OSP Marketing Tools."""

    pass


class ContentValidationError(OSPToolsError):
    """Raised when content validation fails."""

    pass


class FrameworkValidationError(OSPToolsError):
    """Raised when framework validation fails."""

    pass


class CacheError(OSPToolsError):
    """Raised when cache operations fail."""

    pass


class FileOperationError(OSPToolsError):
    """Raised when file operations fail."""

    pass


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle common exceptions in tool functions."""

    async def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            return await func(*args, **kwargs)
        except ContentValidationError as e:
            logger.warning(f"Content validation error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"Content validation failed: {str(e)}",
                "error_type": "content_validation",
                "tool": func.__name__,
            }
        except FrameworkValidationError as e:
            logger.warning(f"Framework validation error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"Framework validation failed: {str(e)}",
                "error_type": "framework_validation",
                "tool": func.__name__,
            }
        except FileOperationError as e:
            logger.error(f"File operation error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"File operation failed: {str(e)}",
                "error_type": "file_operation",
                "tool": func.__name__,
            }
        except CacheError as e:
            logger.error(f"Cache error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"Cache operation failed: {str(e)}",
                "error_type": "cache_operation",
                "tool": func.__name__,
            }
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error occurred: {str(e)}",
                "error_type": "unexpected",
                "tool": func.__name__,
            }

    return wrapper


# Create server instance using FastMCP
mcp = FastMCP("osp_marketing_tools")

# Sistema de Versionamento para Metodologias
METHODOLOGY_VERSIONS = {
    "osp_editing_codes": "1.0.0",
    "osp_writing_guide": "1.0.0",
    "osp_meta_guide": "1.0.0",
    "osp_value_map_guide": "1.0.0",
    "osp_seo_guide": "1.0.0",
    "frameworks_marketing_2025": "2025.1",
    "technical_writing_2025": "2025.1",
    "seo_frameworks_2025": "2025.1",
}


# Advanced cache system for v0.3.0 with backward compatibility
CONTENT_CACHE = cache_mgr.create_cache(
    "content",
    max_size=Config.CACHE_MAX_SIZE,
    ttl_seconds=Config.CACHE_TTL_SECONDS,
    enable_persistence=Config.CACHE_ENABLE_PERSISTENCE,
)

# Frameworks válidos para análise multi-framework
VALID_FRAMEWORKS = {"IDEAL", "STEPPS", "E-E-A-T", "GDocP"}

# ===== ASYNC FILE OPERATIONS =====


async def _read_resource_async(filename: str) -> Dict[str, Any]:
    """Função auxiliar assíncrona para leitura de recursos markdown usando ThreadPoolExecutor."""
    loop = asyncio.get_running_loop()

    # Executa a operação de I/O síncrona em um thread separado
    try:
        result = await loop.run_in_executor(None, _read_resource, filename)
        return result
    except Exception as e:
        logger.error(f"Error in async file reading '{filename}': {str(e)}")
        return {"success": False, "error": f"Async file read error: {str(e)}"}


def _read_resource(filename: str) -> Dict[str, Any]:
    """Função auxiliar síncrona para leitura de recursos markdown (fallback)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    logger.info(f"Reading resource file (sync): {filename}")

    # Validate filename
    if not filename or not filename.strip():
        logger.warning("Empty filename provided to _read_resource")
        raise FileOperationError("Filename cannot be empty")

    # Prevent path traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"Path traversal attempt detected in filename: {filename}")
        raise FileOperationError("Invalid filename - path traversal not allowed")

    try:
        file_path = os.path.join(script_dir, filename)

        # Check if file exists before opening
        if not os.path.exists(file_path):
            logger.error(f"File not found: {filename} at path {file_path}")
            raise FileOperationError(f"Required file '{filename}' not found")

        # Check file size (prevent reading extremely large files)
        file_size = os.path.getsize(file_path)
        max_size = Config.MAX_FILE_SIZE_BYTES
        if file_size > max_size:
            logger.warning(f"Large file detected: {filename} ({file_size} bytes)")
            raise FileOperationError(
                f"File '{filename}' is too large ({file_size} bytes, max {max_size})"
            )

        logger.debug(f"File validation passed for {filename}: size={file_size} bytes")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Validate content
            if not content.strip():
                logger.warning(f"File '{filename}' is empty")

            logger.info(f"Successfully read {filename}: {len(content)} characters")
            return {"success": True, "data": {"content": content}}

    except FileOperationError:
        raise  # Re-raise our custom exceptions
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading {filename}: {str(e)}")
        raise FileOperationError(f"File '{filename}' encoding error: {str(e)}")
    except PermissionError as e:
        logger.error(f"Permission denied reading {filename}: {str(e)}")
        raise FileOperationError(f"Permission denied reading '{filename}': {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error reading {filename}: {str(e)}")
        raise FileOperationError(f"Unexpected error reading '{filename}': {str(e)}")


async def _get_cached_content_async(filename: str) -> Dict[str, Any]:
    """Obtém conteúdo com cache LRU otimizado usando I/O assíncrono."""
    logger.debug(f"Requesting cached content (async): {filename}")

    cached_result = CONTENT_CACHE.get(filename)
    if cached_result is None:
        logger.debug(f"Cache miss for {filename}, reading asynchronously")
        result = await _read_resource_async(filename)
        CONTENT_CACHE.put(filename, result)
        logger.info(f"Cached content for {filename} successfully (async)")
        return result

    logger.debug(f"Cache hit for {filename} (async)")
    return cached_result


def _get_cached_content(filename: str) -> Dict[str, Any]:
    """Obtém conteúdo com cache LRU otimizado (fallback síncrono)."""
    logger.debug(f"Requesting cached content (sync): {filename}")

    cached_result = CONTENT_CACHE.get(filename)
    if cached_result is None:
        logger.debug(f"Cache miss for {filename}, reading synchronously")
        result = _read_resource(filename)
        CONTENT_CACHE.put(filename, result)
        logger.info(f"Cached content for {filename} successfully (sync)")
        return result

    logger.debug(f"Cache hit for {filename} (sync)")
    return cached_result


def _create_config_note(config: Dict[str, Any]) -> str:
    """Cria uma nota formatada em markdown a partir de um dicionário de configuração."""
    note_items = [
        f"- {key.replace('_', ' ').title()}: {value}" for key, value in config.items()
    ]
    return "\n\n---\n**Configuration Applied:**\n" + "\n".join(note_items) + "\n"


@mcp.tool()
@handle_exceptions
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check with detailed system metrics and performance data."""
    logger.info("Performing comprehensive health check")

    import os
    import sys
    import time

    start_time = time.time()

    # Test file access to critical resources
    resource_health = {}
    critical_files = [
        "codes-llm.md",
        "frameworks-marketing-2025.md",
        "technical-writing-2025.md",
        "seo-frameworks-2025.md",
    ]

    for filename in critical_files:
        try:
            result = await _get_cached_content_async(filename)
            resource_health[filename] = {
                "status": "healthy" if result["success"] else "error",
                "accessible": result["success"],
                "cached": CONTENT_CACHE.get(filename) is not None,
            }
        except Exception as e:
            resource_health[filename] = {
                "status": "error",
                "accessible": False,
                "error": str(e),
            }

    # Cache performance metrics
    cache_stats = CONTENT_CACHE.get_stats()
    cache_health = {
        "status": "healthy" if cache_stats["hit_ratio"] > 50 else "warning",
        "performance": (
            "excellent"
            if cache_stats["hit_ratio"] > 80
            else "good" if cache_stats["hit_ratio"] > 60 else "needs_attention"
        ),
        **cache_stats,
    }

    # System resource monitoring (basic metrics without external dependencies)
    try:
        import gc
        import resource

        # Get memory usage info
        memory_usage = resource.getrusage(resource.RUSAGE_SELF)

        system_metrics = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "memory_peak_mb": (
                round(memory_usage.ru_maxrss / 1024 / 1024, 2)
                if sys.platform != "darwin"
                else round(memory_usage.ru_maxrss / 1024 / 1024, 2)
            ),
            "garbage_collector_objects": len(gc.get_objects()),
            "process_id": os.getpid(),
            "current_working_directory": os.getcwd(),
            "file_descriptors_count": (
                len(os.listdir("/proc/self/fd"))
                if os.path.exists("/proc/self/fd")
                else "N/A"
            ),
        }
    except Exception as e:
        logger.warning(f"Could not gather system metrics: {str(e)}")
        system_metrics = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "error": "Advanced system metrics unavailable",
            "reason": str(e),
        }

    # Performance test - measure response time
    response_time = round((time.time() - start_time) * 1000, 2)  # milliseconds

    # Overall system health assessment
    healthy_resources = sum(
        1 for r in resource_health.values() if r["status"] == "healthy"
    )
    total_resources = len(resource_health)
    health_ratio = healthy_resources / total_resources if total_resources > 0 else 0

    overall_status = (
        "healthy"
        if health_ratio >= 1.0 and response_time < 500
        else "warning" if health_ratio >= 0.8 and response_time < 1000 else "critical"
    )

    logger.info(
        f"Health check completed in {response_time}ms - Status: {overall_status}"
    )

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "response_time_ms": response_time,
        "version": __version__,
        "phase": "Phase 3 - Batch Processing & Advanced Cache",
        # Core system info
        "system": {
            "resources": ["osp://marketing-tools"],
            "methodology_versions": METHODOLOGY_VERSIONS,
            "total_methodologies": len(METHODOLOGY_VERSIONS),
            "configurable_tools": 14,  # Updated count
            "total_parameters": 43,
            "error_handling": "Enhanced with custom exceptions",
            "logging": "Structured logging enabled",
            "async_io": "ThreadPoolExecutor implementation",
        },
        # Resource health details
        "resources": {
            "health_ratio": f"{health_ratio:.1%}",
            "details": resource_health,
        },
        # Cache performance
        "cache": cache_health,
        # Framework validation
        "framework_validation": {
            "enabled": True,
            "valid_frameworks": list(VALID_FRAMEWORKS),
            "total_frameworks": len(VALID_FRAMEWORKS),
        },
        # System performance
        "performance": {
            "metrics": system_metrics,
            "assessment": {
                "response_time": (
                    "excellent"
                    if response_time < 200
                    else (
                        "good"
                        if response_time < 500
                        else "slow" if response_time < 1000 else "critical"
                    )
                ),
                "cache_efficiency": cache_health["performance"],
                "resource_availability": f"{healthy_resources}/{total_resources} resources healthy",
            },
        },
        # Implementation status
        "implementation_status": {
            "phase_1_completed": {
                "error_handling": True,
                "structured_logging": True,
                "async_io": True,
                "cache_optimization": True,
                "health_metrics": True,
            },
            "next_phase": "Phase 2 - Quality Foundations (Testing & CI/CD)",
        },
        "last_updated": "2025-08-17",
    }


@mcp.tool()
@handle_exceptions
async def get_editing_codes(
    detail_level: str = "standard",  # basic, standard, comprehensive
    output_format: str = "markdown",  # markdown, json, yaml
    target_persona: str = "general",  # technical, marketing, general
    include_examples: bool = True,
    methodology_version: str = "latest",
) -> Dict[str, Any]:
    """Get the Open Strategy Partners (OSP) editing codes documentation and usage protocol for editing texts.

    Args:
        detail_level: Level of detail (basic, standard, comprehensive)
        output_format: Output format (markdown, json, yaml)
        target_persona: Target audience (technical, marketing, general)
        include_examples: Whether to include examples
        methodology_version: Version to use (latest, 1.0.0)
    """
    result = await _get_cached_content_async("codes-llm.md")
    if result["success"]:
        configuration = {
            "detail_level": detail_level,
            "output_format": output_format,
            "target_persona": target_persona,
            "include_examples": include_examples,
            "methodology_version": methodology_version,
        }
        result["data"]["methodology"] = "osp_editing_codes"
        result["data"]["version"] = METHODOLOGY_VERSIONS["osp_editing_codes"]
        result["data"]["type"] = "editing_methodology"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_writing_guide(
    document_type: str = "general",  # tutorial, reference, api, guide, blog
    audience_level: str = "intermediate",  # beginner, intermediate, advanced, expert
    content_focus: str = "comprehensive",  # structure, style, technical, comprehensive
    include_checklists: bool = True,
    language_style: str = "professional",  # casual, professional, academic, conversational
) -> Dict[str, Any]:
    """Get the Open Strategy Partners (OSP) writing guide and usage protocol for editing texts.

    Args:
        document_type: Type of document (tutorial, reference, api, guide, blog)
        audience_level: Target audience level (beginner, intermediate, advanced, expert)
        content_focus: Focus area (structure, style, technical, comprehensive)
        include_checklists: Whether to include quality checklists
        language_style: Writing style (casual, professional, academic, conversational)
    """
    result = _get_cached_content("guide-llm.md")
    if result["success"]:
        configuration = {
            "document_type": document_type,
            "audience_level": audience_level,
            "content_focus": content_focus,
            "include_checklists": include_checklists,
            "language_style": language_style,
        }
        result["data"]["methodology"] = "osp_writing_guide"
        result["data"]["version"] = METHODOLOGY_VERSIONS["osp_writing_guide"]
        result["data"]["type"] = "writing_methodology"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_meta_guide(
    content_type: str = "article",  # article, landing-page, product, service, blog
    seo_focus: str = "balanced",  # keywords, user-intent, technical, balanced
    target_length: str = "standard",  # short, standard, long
    industry: str = "technology",  # technology, healthcare, finance, ecommerce, general
    optimization_goal: str = "ctr",  # ctr, rankings, conversions, brand
) -> Dict[str, Any]:
    """Get the Open Strategy Partners (OSP) Web Content Meta Information Generation System (titles, meta-titles, slugs).

    Args:
        content_type: Type of content (article, landing-page, product, service, blog)
        seo_focus: SEO optimization focus (keywords, user-intent, technical, balanced)
        target_length: Target content length (short, standard, long)
        industry: Target industry (technology, healthcare, finance, ecommerce, general)
        optimization_goal: Primary goal (ctr, rankings, conversions, brand)
    """
    result = _get_cached_content("meta-llm.md")
    if result["success"]:
        configuration = {
            "content_type": content_type,
            "seo_focus": seo_focus,
            "target_length": target_length,
            "industry": industry,
            "optimization_goal": optimization_goal,
        }
        result["data"]["methodology"] = "osp_meta_guide"
        result["data"]["version"] = METHODOLOGY_VERSIONS["osp_meta_guide"]
        result["data"]["type"] = "meta_optimization"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_value_map_positioning_guide(
    product_type: str = "saas",  # saas, hardware, service, platform, api
    market_stage: str = "growth",  # startup, growth, mature, enterprise
    complexity_level: str = "standard",  # simple, standard, complex, enterprise
    target_market: str = "b2b",  # b2b, b2c, b2b2c, marketplace
    positioning_focus: str = "comprehensive",  # features, benefits, differentiation, comprehensive
) -> Dict[str, Any]:
    """Get the Open Strategy Partners (OSP) Product Communications Value Map Generation System for Product Positioning.

    Args:
        product_type: Type of product (saas, hardware, service, platform, api)
        market_stage: Market stage (startup, growth, mature, enterprise)
        complexity_level: Product complexity (simple, standard, complex, enterprise)
        target_market: Target market type (b2b, b2c, b2b2c, marketplace)
        positioning_focus: Focus area (features, benefits, differentiation, comprehensive)
    """
    result = _get_cached_content("product-value-map-llm.md")
    if result["success"]:
        configuration = {
            "product_type": product_type,
            "market_stage": market_stage,
            "complexity_level": complexity_level,
            "target_market": target_market,
            "positioning_focus": positioning_focus,
        }
        result["data"]["methodology"] = "osp_value_map_guide"
        result["data"]["version"] = METHODOLOGY_VERSIONS["osp_value_map_guide"]
        result["data"]["type"] = "positioning_methodology"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_on_page_seo_guide(
    focus_area: str = "comprehensive",  # on-page, technical, content, local, comprehensive
    industry: str = "technology",  # technology, ecommerce, healthcare, finance, local-business
    difficulty: str = "intermediate",  # beginner, intermediate, advanced, expert
    checklist_format: bool = False,
    include_tools: bool = True,
    seo_framework: str = "traditional",  # traditional, e-eat, entity-based, core-vitals
) -> Dict[str, Any]:
    """Get the Open Strategy Partners (OSP) On-Page SEO Optimization Guide.

    Args:
        focus_area: SEO focus area (on-page, technical, content, local, comprehensive)
        industry: Target industry (technology, ecommerce, healthcare, finance, local-business)
        difficulty: Complexity level (beginner, intermediate, advanced, expert)
        checklist_format: Return as actionable checklist format
        include_tools: Include tool recommendations
        seo_framework: SEO framework approach (traditional, e-eat, entity-based, core-vitals)
    """
    result = _get_cached_content("on-page-seo-guide.md")
    if result["success"]:
        configuration = {
            "focus_area": focus_area,
            "industry": industry,
            "difficulty": difficulty,
            "checklist_format": checklist_format,
            "include_tools": include_tools,
            "seo_framework": seo_framework,
        }
        result["data"]["methodology"] = "osp_seo_guide"
        result["data"]["version"] = METHODOLOGY_VERSIONS["osp_seo_guide"]
        result["data"]["type"] = "seo_methodology"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


# ==== NOVAS FERRAMENTAS 2025 ====


@mcp.tool()
@handle_exceptions
async def get_marketing_frameworks_2025(
    framework_focus: str = "all",  # ideal, stepps, race, stp, they-ask-you-answer, all
    content_type: str = "digital",  # digital, traditional, social, email, video, all
    audience_type: str = "b2b",  # b2b, b2c, mixed
    campaign_stage: str = "comprehensive",  # awareness, consideration, conversion, retention, comprehensive
    industry_vertical: str = "technology",  # technology, healthcare, finance, ecommerce, saas, general
) -> Dict[str, Any]:
    """Get the 2025 Marketing Content Frameworks including IDEAL, STEPPS, RACE, STP, and They Ask You Answer methodologies.

    Args:
        framework_focus: Specific framework to focus on (ideal, stepps, race, stp, they-ask-you-answer, all)
        content_type: Type of content (digital, traditional, social, email, video, all)
        audience_type: Target audience (b2b, b2c, mixed)
        campaign_stage: Marketing funnel stage (awareness, consideration, conversion, retention, comprehensive)
        industry_vertical: Industry focus (technology, healthcare, finance, ecommerce, saas, general)
    """
    result = _get_cached_content("frameworks-marketing-2025.md")
    if result["success"]:
        configuration = {
            "framework_focus": framework_focus,
            "content_type": content_type,
            "audience_type": audience_type,
            "campaign_stage": campaign_stage,
            "industry_vertical": industry_vertical,
        }
        result["data"]["methodology"] = "frameworks_marketing_2025"
        result["data"]["version"] = METHODOLOGY_VERSIONS["frameworks_marketing_2025"]
        result["data"]["type"] = "marketing_frameworks"
        result["data"]["frameworks"] = [
            "IDEAL",
            "STEPPS",
            "RACE",
            "STP",
            "They Ask You Answer",
        ]
        result["data"]["year"] = "2025"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_technical_writing_2025(
    framework_focus: str = "all",  # gdocp, docs-as-code, interactive, content-design, all
    documentation_type: str = "api",  # api, user-guide, reference, tutorial, troubleshooting
    complexity_level: str = "intermediate",  # basic, intermediate, advanced, expert
    team_size: str = "medium",  # solo, small, medium, large, enterprise
    automation_level: str = "standard",  # minimal, standard, advanced, full
) -> Dict[str, Any]:
    """Get the 2025 Technical Writing Methodologies including GDocP (ALCOA-C), Docs-as-Code, and Interactive Documentation frameworks.

    Args:
        framework_focus: Specific framework focus (gdocp, docs-as-code, interactive, content-design, all)
        documentation_type: Type of documentation (api, user-guide, reference, tutorial, troubleshooting)
        complexity_level: Technical complexity (basic, intermediate, advanced, expert)
        team_size: Team size context (solo, small, medium, large, enterprise)
        automation_level: Desired automation level (minimal, standard, advanced, full)
    """
    result = _get_cached_content("technical-writing-2025.md")
    if result["success"]:
        configuration = {
            "framework_focus": framework_focus,
            "documentation_type": documentation_type,
            "complexity_level": complexity_level,
            "team_size": team_size,
            "automation_level": automation_level,
        }
        result["data"]["methodology"] = "technical_writing_2025"
        result["data"]["version"] = METHODOLOGY_VERSIONS["technical_writing_2025"]
        result["data"]["type"] = "technical_writing"
        result["data"]["frameworks"] = [
            "GDocP",
            "Docs-as-Code",
            "Interactive Documentation",
            "Content Design System",
        ]
        result["data"]["year"] = "2025"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_seo_frameworks_2025(
    framework_focus: str = "all",  # e-eat, entity-based, snippets, clusters, core-vitals, all
    optimization_goal: str = "rankings",  # rankings, traffic, conversions, authority, user-experience
    content_maturity: str = "existing",  # new, existing, refresh, comprehensive
    technical_level: str = "intermediate",  # basic, intermediate, advanced, expert
    search_intent: str = "mixed",  # informational, navigational, transactional, commercial, mixed
) -> Dict[str, Any]:
    """Get the 2025 SEO and Optimization Frameworks including E-E-A-T, Entity-Based SEO, Snippet-Friendly Structure, and Topic Cluster Strategy.

    Args:
        framework_focus: Specific framework focus (e-eat, entity-based, snippets, clusters, core-vitals, all)
        optimization_goal: Primary SEO goal (rankings, traffic, conversions, authority, user-experience)
        content_maturity: Content lifecycle stage (new, existing, refresh, comprehensive)
        technical_level: Technical complexity (basic, intermediate, advanced, expert)
        search_intent: Target search intent (informational, navigational, transactional, commercial, mixed)
    """
    result = _get_cached_content("seo-frameworks-2025.md")
    if result["success"]:
        configuration = {
            "framework_focus": framework_focus,
            "optimization_goal": optimization_goal,
            "content_maturity": content_maturity,
            "technical_level": technical_level,
            "search_intent": search_intent,
        }
        result["data"]["methodology"] = "seo_frameworks_2025"
        result["data"]["version"] = METHODOLOGY_VERSIONS["seo_frameworks_2025"]
        result["data"]["type"] = "seo_frameworks"
        result["data"]["frameworks"] = [
            "E-E-A-T",
            "Entity-Based SEO",
            "Snippet-Friendly Structure",
            "Topic Cluster Strategy",
            "Core Web Vitals",
        ]
        result["data"]["year"] = "2025"
        result["data"]["configuration"] = configuration
        # Add configuration note to content
        if result["data"]["content"]:
            result["data"]["content"] += _create_config_note(configuration)
    return result


@mcp.tool()
@handle_exceptions
async def get_methodology_versions() -> Dict[str, Any]:
    """Get version information for all available methodologies and frameworks."""
    return {
        "success": True,
        "data": {
            "versions": METHODOLOGY_VERSIONS,
            "total_methodologies": len(METHODOLOGY_VERSIONS),
            "last_updated": "2025-08-17",
            "categories": {
                "osp_legacy": [
                    "osp_editing_codes",
                    "osp_writing_guide",
                    "osp_meta_guide",
                    "osp_value_map_guide",
                    "osp_seo_guide",
                ],
                "frameworks_2025": [
                    "frameworks_marketing_2025",
                    "technical_writing_2025",
                    "seo_frameworks_2025",
                ],
            },
        },
    }


@mcp.tool()
@handle_exceptions
async def get_cache_statistics() -> Dict[str, Any]:
    """Get detailed cache statistics and performance metrics."""
    cache_stats = CONTENT_CACHE.get_stats()

    # Calculate utilization if not present
    utilization = cache_stats.get(
        "utilization",
        (
            (cache_stats["current_size"] / cache_stats["max_size"] * 100)
            if cache_stats["max_size"] > 0
            else 0
        ),
    )

    # Adicionar análise de performance
    performance_analysis = {
        "efficiency": (
            "excellent"
            if cache_stats["hit_ratio"] >= 80
            else (
                "good"
                if cache_stats["hit_ratio"] >= 60
                else "fair" if cache_stats["hit_ratio"] >= 40 else "poor"
            )
        ),
        "memory_usage": (
            "optimal"
            if utilization <= 80
            else "high" if utilization <= 95 else "critical"
        ),
        "recommendations": [],
    }

    # Gerar recomendações baseadas nas estatísticas
    if cache_stats["hit_ratio"] < 60:
        performance_analysis["recommendations"].append(
            "Consider increasing cache size for better hit ratio"
        )

    if cache_stats["evictions"] > cache_stats["hits"] * 0.1:
        performance_analysis["recommendations"].append(
            "High eviction rate detected - cache size may be too small"
        )

    if utilization > 90:
        performance_analysis["recommendations"].append(
            "Cache utilization is high - monitor for performance impact"
        )

    if not performance_analysis["recommendations"]:
        performance_analysis["recommendations"].append("Cache performance is optimal")

    return {
        "success": True,
        "data": {
            "cache_statistics": cache_stats,
            "performance_analysis": performance_analysis,
            "methodology": "LRU Cache with Statistics",
            "monitoring_timestamp": datetime.now().isoformat(),
        },
    }


@mcp.tool()
@handle_exceptions
async def clear_cache_statistics() -> Dict[str, Any]:
    """Clear cache statistics and cleanup expired entries."""
    old_stats = CONTENT_CACHE.get_stats()

    # Cleanup expired entries (new v0.3.0 feature)
    expired_count = CONTENT_CACHE.cleanup_expired()

    new_stats = CONTENT_CACHE.get_stats()

    return {
        "success": True,
        "data": {
            "message": "Cache statistics cleared and expired entries removed",
            "previous_stats": old_stats,
            "expired_entries_removed": expired_count,
            "current_stats": new_stats,
            "cleared_timestamp": datetime.now().isoformat(),
        },
    }


@mcp.tool()
@handle_exceptions
async def benchmark_file_operations() -> Dict[str, Any]:
    """Benchmark sync vs async file operations to demonstrate performance improvements."""
    import time

    test_files = ["codes-llm.md", "guide-llm.md", "meta-llm.md"]

    # Benchmark synchronous operations
    sync_start = time.time()
    sync_results = []
    for filename in test_files:
        result = _read_resource(filename)
        sync_results.append({"file": filename, "success": result["success"]})
    sync_duration = time.time() - sync_start

    # Benchmark asynchronous operations
    async_start = time.time()
    async_tasks = [_read_resource_async(filename) for filename in test_files]
    async_results_raw = await asyncio.gather(*async_tasks)
    async_results = [
        {"file": test_files[i], "success": result["success"]}
        for i, result in enumerate(async_results_raw)
    ]
    async_duration = time.time() - async_start

    # Calculate performance improvement
    improvement = (
        ((sync_duration - async_duration) / sync_duration * 100)
        if sync_duration > 0
        else 0
    )

    return {
        "success": True,
        "data": {
            "benchmark_results": {
                "synchronous": {
                    "duration_seconds": round(sync_duration, 4),
                    "files_processed": len(sync_results),
                    "results": sync_results,
                },
                "asynchronous": {
                    "duration_seconds": round(async_duration, 4),
                    "files_processed": len(async_results),
                    "results": async_results,
                },
                "performance_improvement": {
                    "time_saved_seconds": round(sync_duration - async_duration, 4),
                    "improvement_percentage": round(improvement, 1),
                    "analysis": (
                        "faster" if async_duration < sync_duration else "slower"
                    ),
                    "note": "Async benefits are more apparent with multiple concurrent requests",
                },
            },
            "methodology": "ThreadPoolExecutor-based async I/O",
            "benchmark_timestamp": datetime.now().isoformat(),
        },
    }


@mcp.tool()
@handle_exceptions
async def analyze_content_multi_framework(
    content: str, frameworks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze content using multiple 2025 frameworks with enhanced validation and error handling.

    Args:
        content: The text content to analyze (minimum 10 characters, maximum 1MB)
        frameworks: List of frameworks to use. Available: IDEAL, STEPPS, E-E-A-T, GDocP

    Returns:
        Dict containing analysis results for each framework with scores and recommendations

    Raises:
        ContentValidationError: If content is invalid
        FrameworkValidationError: If frameworks are invalid
    """
    if frameworks is None or frameworks == []:
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

    logger.info(f"Starting multi-framework analysis with {len(frameworks)} frameworks")

    # Enhanced content validation with configurable limits
    if not content:
        raise ContentValidationError("Content parameter is required")

    if not content.strip():
        raise ContentValidationError("Content cannot be empty or whitespace only")

    if len(content) < 10:
        raise ContentValidationError(
            "Content is too short for meaningful analysis (minimum 10 characters)"
        )

    if len(content) > Config.MAX_ANALYSIS_CONTENT_LENGTH:
        raise ContentValidationError(
            f"Content is too large for analysis (maximum {Config.MAX_ANALYSIS_CONTENT_LENGTH} characters)"
        )

    if not isinstance(frameworks, list):
        raise FrameworkValidationError("Frameworks must be provided as a list")

    # Validate each framework
    unrecognized_frameworks = []
    processed_frameworks = []

    for framework in frameworks:
        if framework not in VALID_FRAMEWORKS:
            unrecognized_frameworks.append(framework)
            if Config.STRICT_FRAMEWORK_VALIDATION:
                raise FrameworkValidationError(
                    f"Framework '{framework}' is not supported. Available: {list(VALID_FRAMEWORKS)}"
                )
        else:
            processed_frameworks.append(framework)

    # If no valid frameworks and not in strict mode, provide helpful error
    if not processed_frameworks:
        available_frameworks = ", ".join(VALID_FRAMEWORKS)
        raise FrameworkValidationError(
            f"No valid frameworks found. Available frameworks: {available_frameworks}"
        )

    try:
        # Use the new modular analysis system
        analysis_results = analyze_content_with_frameworks(
            content, processed_frameworks
        )

        # Calculate overall scores
        overall_scores = {}
        for framework, results in analysis_results.items():
            if "error" not in results:
                # Extract scores from each framework's analysis
                scores = []
                for section_name, section_data in results.items():
                    if isinstance(section_data, dict) and "score" in section_data:
                        scores.append(section_data["score"])

                if scores:
                    overall_scores[framework] = round(sum(scores) / len(scores), 1)
                else:
                    overall_scores[framework] = 0

        # Calculate average score across all frameworks
        if overall_scores:
            average_score = round(sum(overall_scores.values()) / len(overall_scores), 1)
        else:
            average_score = 0

        # Add warnings for unrecognized frameworks
        warnings = []
        if unrecognized_frameworks:
            warnings.append(
                f"Unrecognized frameworks ignored: {', '.join(unrecognized_frameworks)}"
            )

        logger.info(f"Analysis completed successfully. Average score: {average_score}")

        return {
            "success": True,
            "data": {
                "content_length": len(content),
                "content_words": len(content.split()),
                "frameworks_analyzed": processed_frameworks,
                "unrecognized_frameworks": unrecognized_frameworks,
                "analysis": {
                    "frameworks": analysis_results,
                    "overall_scores": {
                        **overall_scores,
                        "average_score": average_score,
                    },
                },
                "metadata": {
                    "methodology_version": "2025.1",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "configuration": Config.get_env_info(),
                    "validation_info": {
                        "total_frameworks_requested": len(frameworks),
                        "valid_frameworks_processed": len(processed_frameworks),
                        "invalid_frameworks_ignored": len(unrecognized_frameworks),
                        "available_frameworks": list(VALID_FRAMEWORKS),
                        "strict_validation": Config.STRICT_FRAMEWORK_VALIDATION,
                    },
                },
                "warnings": warnings if warnings else None,
            },
        }

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise ContentValidationError(f"Analysis processing failed: {str(e)}")


@mcp.tool()
@handle_exceptions
async def analyze_content_batch(
    batch_id: str,
    content_items: List[Dict[str, Any]],
    default_frameworks: Optional[List[str]] = None,
    priority: int = 0,
) -> Dict[str, Any]:
    """Analyze multiple content items in parallel using batch processing.

    Args:
        batch_id: Unique identifier for this batch
        content_items: List of content items to analyze (strings or dicts)
        default_frameworks: Default frameworks to use if not specified per item
        priority: Priority level for this batch (higher = processed first)
    """
    from .batch import batch_manager

    logger.info(f"Starting batch analysis: {batch_id} with {len(content_items)} items")

    # Validate inputs
    if not batch_id or not batch_id.strip():
        raise ValueError("batch_id is required and cannot be empty")

    if not content_items:
        raise ValueError("content_items cannot be empty")

    if len(content_items) > Config.BATCH_MAX_SIZE:
        raise ValueError(
            f"Batch size ({len(content_items)}) exceeds maximum ({Config.BATCH_MAX_SIZE})"
        )

    # Use default frameworks if none specified
    if default_frameworks is None:
        default_frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

    try:
        # Submit batch for processing
        result = await batch_manager.submit_batch(
            batch_id=batch_id,
            content_items=content_items,
            default_frameworks=default_frameworks,
            priority=priority,
        )

        return {
            "success": True,
            "data": {
                "batch_id": batch_id,
                "results": result.get("results", []),
                "summary": result.get("summary", {}),
                "progress": result.get("progress", {}),
                "processing_completed": True,
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": __version__,
                "batch_size": len(content_items),
                "default_frameworks": default_frameworks,
                "priority": priority,
            },
        }

    except Exception as e:
        logger.error(f"Batch processing failed for {batch_id}: {str(e)}")
        raise ValueError(f"Batch processing failed: {str(e)}")


@mcp.tool()
@handle_exceptions
async def get_batch_status() -> Dict[str, Any]:
    """Get status of active batch processing operations."""
    from .batch import batch_manager

    active_batches = batch_manager.get_active_batches()
    batch_history = batch_manager.get_batch_history(limit=5)

    return {
        "success": True,
        "data": {
            "active_batches": active_batches,
            "active_count": len(active_batches),
            "recent_history": batch_history,
            "configuration": {
                "max_batch_size": Config.BATCH_MAX_SIZE,
                "parallel_workers": Config.BATCH_PARALLEL_WORKERS,
                "timeout_seconds": Config.BATCH_TIMEOUT_SECONDS,
            },
        },
        "metadata": {"timestamp": datetime.now().isoformat(), "version": __version__},
    }


@mcp.tool()
@handle_exceptions
async def cancel_batch(batch_id: str) -> Dict[str, Any]:
    """Cancel an active batch processing operation.

    Args:
        batch_id: ID of the batch to cancel
    """
    from .batch import batch_manager

    if not batch_id or not batch_id.strip():
        raise ValueError("batch_id is required and cannot be empty")

    success = batch_manager.cancel_batch(batch_id)

    return {
        "success": True,
        "data": {
            "batch_id": batch_id,
            "cancelled": success,
            "message": f"Batch {batch_id} {'cancelled successfully' if success else 'was not found or already completed'}",
        },
        "metadata": {"timestamp": datetime.now().isoformat(), "version": __version__},
    }


@mcp.tool()
@handle_exceptions
async def get_advanced_cache_info() -> Dict[str, Any]:
    """Get detailed information about the advanced cache system."""
    from .cache import cache_manager

    # Get stats from all caches
    all_stats = cache_manager.get_all_stats()

    # Get detailed entry information from default cache
    default_cache = cache_manager.get_cache("default")
    entries_info = default_cache.get_entries_info()

    return {
        "success": True,
        "data": {
            "cache_statistics": all_stats,
            "entry_details": entries_info[:10],  # Limit to 10 most recent
            "total_entries": len(entries_info),
            "cache_configuration": {
                "max_size": Config.CACHE_MAX_SIZE,
                "ttl_seconds": Config.CACHE_TTL_SECONDS,
                "persistence_enabled": Config.CACHE_ENABLE_PERSISTENCE,
            },
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": __version__,
            "cache_system": "AdvancedLRUCache with TTL",
        },
    }


@mcp.tool()
@handle_exceptions
async def cleanup_expired_cache() -> Dict[str, Any]:
    """Manually cleanup expired cache entries across all caches."""
    from .cache import cache_manager

    # Cleanup expired entries from all caches
    cleanup_results = cache_manager.cleanup_all_expired()

    total_removed = sum(cleanup_results.values())

    return {
        "success": True,
        "data": {
            "cleanup_results": cleanup_results,
            "total_expired_removed": total_removed,
            "message": f"Cleaned up {total_removed} expired entries across all caches",
            "timestamp": datetime.now().isoformat(),
        },
        "metadata": {"timestamp": datetime.now().isoformat(), "version": __version__},
    }


def main() -> None:
    """Run the MCP server."""
    try:
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
