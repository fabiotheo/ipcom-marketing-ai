# API Reference - OSP Marketing Tools

## Overview

OSP Marketing Tools provides a Model Context Protocol (MCP) server with tools
for analyzing marketing content using 2025 frameworks. All functions are
asynchronous and return structured JSON responses.

## Base Response Format

All API functions return responses in this format:

```json
{
  "success": boolean,
  "data": object,
  "metadata": object,
  "error": string (only if success=false)
}
```

## Core Analysis Functions

### `analyze_content_multi_framework`

Analyzes content using multiple marketing frameworks simultaneously.

**Signature:**

```python
async def analyze_content_multi_framework(
    content: str,
    frameworks: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters:**

- `content` (str, required): Text content to analyze
  - Minimum: 10 characters
  - Maximum: 1,000,000 characters (1MB)
  - Must contain meaningful text
- `frameworks` (List[str], optional): List of frameworks to use
  - Available: `["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]`
  - Default: All frameworks if not specified

**Returns:**

```json
{
  "success": true,
  "data": {
    "analysis": {
      "frameworks": {
        "IDEAL": {
          "identify": {
            "score": 85.2,
            "recommendations": "Consider adding more specific audience identification..."
          },
          "discover": {
            "score": 78.4,
            "recommendations": "Enhance discovery elements with data-driven insights..."
          },
          "empower": {
            "score": 92.1,
            "recommendations": "Excellent empowerment strategies present..."
          },
          "activate": {
            "score": 67.8,
            "recommendations": "Strengthen call-to-action elements..."
          },
          "learn": {
            "score": 71.5,
            "recommendations": "Add feedback mechanisms and learning loops..."
          }
        },
        "STEPPS": {
          "social_currency": {
            "score": 82.3,
            "recommendations": "Great social value indicators..."
          },
          "triggers": {
            "score": 74.6,
            "recommendations": "Add more environmental cues..."
          },
          "emotion": {
            "score": 88.9,
            "recommendations": "Strong emotional appeal present..."
          },
          "public": {
            "score": 65.2,
            "recommendations": "Increase visibility and shareability..."
          },
          "practical_value": {
            "score": 91.4,
            "recommendations": "Excellent practical utility..."
          },
          "stories": {
            "score": 79.7,
            "recommendations": "Good narrative elements, consider enhancing..."
          }
        }
      },
      "overall_scores": {
        "IDEAL": 78.6,
        "STEPPS": 80.1,
        "E-E-A-T": 75.8,
        "GDocP": 72.3,
        "average_score": 76.7
      }
    },
    "content_length": 1245,
    "frameworks_analyzed": ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]
  },
  "metadata": {
    "processing_time_ms": 156.7,
    "timestamp": "2025-08-17T20:18:00Z",
    "version": "0.3.0",
    "total_frameworks": 4,
    "successful_frameworks": 4,
    "failed_frameworks": 0,
    "content_words": 187,
    "content_length": 1245
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": "Content validation failed: Content too short for meaningful analysis",
  "metadata": {
    "timestamp": "2025-08-17T20:18:00Z",
    "version": "0.3.0"
  }
}
```

**Examples:**

Single framework analysis:

```python
result = await analyze_content_multi_framework(
    content="Expert guide for software developers with practical examples.",
    frameworks=["IDEAL"]
)
```

All frameworks (default):

```python
result = await analyze_content_multi_framework(
    content="Comprehensive marketing guide with expert insights and actionable strategies."
)
```

## Framework Details

### IDEAL Framework

Analyzes content for the IDEAL methodology components:

**Components:**

- `identify`: Audience identification and targeting (0-100)
- `discover`: Insight discovery and opportunity identification (0-100)
- `empower`: User empowerment and enablement (0-100)
- `activate`: Engagement activation and action triggers (0-100)
- `learn`: Learning mechanisms and feedback loops (0-100)

**Analysis Focus:**

- Audience targeting keywords
- Discovery and research elements
- Empowerment language and tools
- Call-to-action effectiveness
- Learning and improvement indicators

### STEPPS Framework

Analyzes content for viral marketing elements:

**Components:**

- `social_currency`: Social status and sharing value (0-100)
- `triggers`: Environmental cues and reminders (0-100)
- `emotion`: Emotional response triggers (0-100)
- `public`: Public visibility and observability (0-100)
- `practical_value`: Useful, actionable information (0-100)
- `stories`: Narrative elements and storytelling (0-100)

**Analysis Focus:**

- Status-enhancing elements
- Contextual triggers
- Emotional language
- Shareability factors
- Practical utility
- Story structure

### E-E-A-T Framework (Google 2025)

Analyzes content for Google's quality guidelines:

**Components:**

- `experience`: Demonstrated practical experience (0-100)
- `expertise`: Subject matter expertise indicators (0-100)
- `authority`: Recognized authority signals (0-100)
- `trustworthiness`: Trust and credibility markers (0-100)

**Analysis Focus:**

- Experience indicators
- Expert credentials
- Authority citations
- Trust signals

### GDocP Framework (Google Docs Policy 2025)

Analyzes content for Google's documentation standards:

**Components:**

- `attributable`: Source attribution and verification (0-100)
- `legible`: Clarity and readability (0-100)
- `contemporaneous`: Current and up-to-date content (0-100)
- `original`: Originality and uniqueness (0-100)
- `accurate`: Factual accuracy and precision (0-100)
- `complete`: Completeness and comprehensiveness (0-100)

**Analysis Focus:**

- Source citations
- Reading clarity
- Freshness indicators
- Original insights
- Factual accuracy
- Content completeness

## System Information Functions

### `health_check`

Returns system health status and basic diagnostics.

**Signature:**

```python
async def health_check() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "status": "healthy",
  "frameworks_available": ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"],
  "test_analysis_success": true,
  "version": "0.3.0",
  "timestamp": "2025-08-17T20:18:00Z"
}
```

### `get_methodology_versions`

Returns versions and details of implemented frameworks.

**Signature:**

```python
async def get_methodology_versions() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "versions": {
    "IDEAL": "2025.1",
    "STEPPS": "2025.1",
    "E-E-A-T": "2025.1",
    "GDocP": "2025.1"
  },
  "metadata": {
    "total_frameworks": 4,
    "last_updated": "2025-08-17",
    "version": "0.3.0"
  }
}
```

## Performance and Cache Functions

### `get_cache_statistics`

Returns cache performance statistics.

**Signature:**

```python
async def get_cache_statistics() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "cache_stats": {
    "total_requests": 1547,
    "cache_hits": 423,
    "cache_misses": 1124,
    "hit_rate": 27.3,
    "cache_size": 42,
    "max_cache_size": 50
  }
}
```

### `clear_cache_statistics`

Clears cache statistics (not the cache itself).

**Signature:**

```python
async def clear_cache_statistics() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "message": "Cache statistics cleared successfully"
}
```

### `benchmark_file_operations`

Runs file operation performance benchmarks.

**Signature:**

```python
async def benchmark_file_operations() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "benchmark_results": {
    "write_time_ms": 2.3,
    "read_time_ms": 1.1,
    "delete_time_ms": 0.8,
    "total_time_ms": 4.2
  }
}
```

## Resource Functions

### `get_editing_codes`

Returns editing codes reference documentation.

**Signature:**

```python
async def get_editing_codes() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "content": "# Editing Codes\n\n## Standard Codes\n...",
  "metadata": {
    "content_type": "markdown",
    "last_modified": "2025-08-17T20:18:00Z"
  }
}
```

### `get_writing_guide`

Returns writing guide documentation.

**Signature:**

```python
async def get_writing_guide() -> Dict[str, Any]
```

### `get_meta_guide`

Returns meta description guide.

**Signature:**

```python
async def get_meta_guide() -> Dict[str, Any]
```

### `get_value_map_positioning_guide`

Returns value map positioning guide.

**Signature:**

```python
async def get_value_map_positioning_guide() -> Dict[str, Any]
```

### `get_on_page_seo_guide`

Returns on-page SEO guide.

**Signature:**

```python
async def get_on_page_seo_guide() -> Dict[str, Any]
```

### `get_marketing_frameworks_2025`

Returns 2025 marketing frameworks documentation.

**Signature:**

```python
async def get_marketing_frameworks_2025() -> Dict[str, Any]
```

### `get_technical_writing_2025`

Returns 2025 technical writing guide.

**Signature:**

```python
async def get_technical_writing_2025() -> Dict[str, Any]
```

### `get_seo_frameworks_2025`

Returns 2025 SEO frameworks documentation.

**Signature:**

```python
async def get_seo_frameworks_2025() -> Dict[str, Any]
```

## Error Handling

### Exception Types

**ContentValidationError**

- Empty or null content
- Content too short (< 10 characters)
- Content too long (> 1MB)

**FrameworkValidationError**

- Invalid framework name
- Framework not available
- Framework configuration error

**FileOperationError**

- Resource file not found
- File read permission denied
- Path traversal attempt

**AnalysisTimeoutError**

- Analysis exceeded timeout limit
- System resource constraints

### Error Response Format

```json
{
  "success": false,
  "error": "Detailed error message with context",
  "error_type": "ContentValidationError",
  "metadata": {
    "timestamp": "2025-08-17T20:18:00Z",
    "version": "0.3.0",
    "function": "analyze_content_multi_framework"
  }
}
```

### Common Error Scenarios

**Empty Content:**

```json
{
  "success": false,
  "error": "Content validation failed: Content parameter is required"
}
```

**Invalid Framework:**

```json
{
  "success": false,
  "error": "Framework validation failed: Framework 'INVALID' is not supported. Available: ['IDEAL', 'STEPPS', 'E-E-A-T', 'GDocP']"
}
```

**Content Too Long:**

```json
{
  "success": false,
  "error": "Content validation failed: Content too long: 2000000 characters (max: 1000000)"
}
```

## Rate Limits and Performance

### Performance Guidelines

| Operation            | Typical Response Time | Max Recommended |
| -------------------- | --------------------- | --------------- |
| Single Framework     | ~4ms                  | < 100ms         |
| Multi Framework (4x) | ~2ms                  | < 200ms         |
| Resource Loading     | ~1ms                  | < 50ms          |
| Cache Operations     | ~0.5ms                | < 10ms          |

### Best Practices

1. **Batch Processing**: Use single multi-framework call instead of multiple
   single-framework calls
2. **Content Size**: Keep content under 100KB for optimal performance
3. **Framework Selection**: Only specify frameworks you need
4. **Caching**: Identical content will benefit from caching
5. **Concurrent Requests**: System handles up to 10 concurrent analyses
   efficiently

### Rate Limiting

- **Default**: No explicit rate limits
- **Recommended**: Max 100 requests/minute per client
- **Concurrent**: Max 10 simultaneous requests
- **Content Size**: 1MB per request maximum

## SDK Integration Examples

### Python Client

```python
import asyncio
from osp_marketing_tools.server import analyze_content_multi_framework

async def analyze_blog_post():
    content = """
    Expert Software Development: A Comprehensive Guide

    This guide provides practical insights for experienced developers
    looking to enhance their skills and deliver high-quality solutions.
    We'll explore advanced techniques, share real-world examples,
    and provide actionable strategies for continuous improvement.
    """

    # Analyze with specific frameworks
    result = await analyze_content_multi_framework(
        content=content,
        frameworks=["IDEAL", "E-E-A-T"]
    )

    if result["success"]:
        scores = result["data"]["analysis"]["overall_scores"]
        print(f"IDEAL Score: {scores['IDEAL']}")
        print(f"E-E-A-T Score: {scores['E-E-A-T']}")
        print(f"Average: {scores['average_score']}")
    else:
        print(f"Analysis failed: {result['error']}")

# Run analysis
asyncio.run(analyze_blog_post())
```

### Batch Analysis

```python
async def analyze_multiple_contents():
    contents = [
        "First article content...",
        "Second blog post content...",
        "Third marketing copy..."
    ]

    # Analyze concurrently
    tasks = [
        analyze_content_multi_framework(content, ["STEPPS"])
        for content in contents
    ]

    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        if result["success"]:
            score = result["data"]["analysis"]["overall_scores"]["STEPPS"]
            print(f"Content {i+1}: {score}")
        else:
            print(f"Content {i+1} failed: {result['error']}")
```

### Error Handling Pattern

```python
async def robust_analysis(content: str):
    try:
        result = await analyze_content_multi_framework(content)

        if not result["success"]:
            print(f"Analysis failed: {result['error']}")
            return None

        return result["data"]["analysis"]["overall_scores"]["average_score"]

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Batch Processing Functions (v0.3.0)

### `analyze_content_batch`

Analyze multiple content items in parallel using the new batch processing
system.

**Signature:**

```python
async def analyze_content_batch(
    batch_id: str,
    content_items: List[Dict[str, Any]],
    default_frameworks: Optional[List[str]] = None,
    priority: int = 0
) -> Dict[str, Any]
```

**Parameters:**

- `batch_id` (str, required): Unique identifier for this batch
  - Must be non-empty string
  - Used for tracking and cancellation
- `content_items` (List[Dict], required): List of content items to analyze
  - Each item can be a string or structured object
  - Structured format:
    ```json
    {
      "id": "optional_custom_id",
      "content": "content to analyze",
      "frameworks": ["IDEAL", "STEPPS"],
      "metadata": { "source": "blog" },
      "priority": 5
    }
    ```
- `default_frameworks` (List[str], optional): Default frameworks for items
  without specified frameworks
  - Available: `["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]`
  - Default: All frameworks
- `priority` (int, optional): Default priority for items (0-10, higher =
  processed first)

**Returns:**

```json
{
  "success": true,
  "data": {
    "batch_id": "my_batch_001",
    "results": [
      {
        "item_id": "my_batch_001_item_0",
        "success": true,
        "data": {
          "IDEAL": {...},
          "STEPPS": {...}
        },
        "processing_time_ms": 150.5,
        "framework_count": 2
      }
    ],
    "summary": {
      "total_items": 5,
      "successful_items": 4,
      "failed_items": 1,
      "success_rate": 80.0,
      "total_processing_time_seconds": 2.3,
      "average_processing_time_ms": 460.0,
      "total_frameworks_processed": 8,
      "throughput_items_per_second": 2.17
    },
    "progress": {
      "total_items": 5,
      "completed_items": 4,
      "failed_items": 1,
      "processing_time_seconds": 2.3
    }
  }
}
```

**Configuration Limits:**

- Maximum batch size: Configurable via `OSP_BATCH_MAX_SIZE` (default: 10)
- Parallel workers: Configurable via `OSP_BATCH_WORKERS` (default: 4)
- Timeout: Configurable via `OSP_BATCH_TIMEOUT` (default: 300 seconds)

### `get_batch_status`

Get status of active batch processing operations and recent history.

**Signature:**

```python
async def get_batch_status() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "data": {
    "active_batches": ["batch_001", "batch_002"],
    "active_count": 2,
    "recent_history": [
      {
        "batch_id": "batch_000",
        "timestamp": 1692387600.0,
        "summary": {
          "total_items": 3,
          "successful_items": 3,
          "success_rate": 100.0
        },
        "success": true
      }
    ],
    "configuration": {
      "max_batch_size": 10,
      "parallel_workers": 4,
      "timeout_seconds": 300
    }
  }
}
```

### `cancel_batch`

Cancel an active batch processing operation.

**Signature:**

```python
async def cancel_batch(batch_id: str) -> Dict[str, Any]
```

**Parameters:**

- `batch_id` (str, required): ID of the batch to cancel

**Returns:**

```json
{
  "success": true,
  "data": {
    "batch_id": "batch_001",
    "cancelled": true,
    "message": "Batch batch_001 cancelled successfully"
  }
}
```

## Advanced Cache Functions (v0.3.0)

### `get_advanced_cache_info`

Get detailed information about the advanced cache system including TTL,
persistence, and multiple cache instances.

**Signature:**

```python
async def get_advanced_cache_info() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "data": {
    "cache_statistics": {
      "default": {
        "hits": 245,
        "misses": 82,
        "hit_ratio": 74.92,
        "evictions": 5,
        "expired_removals": 12,
        "current_size": 45,
        "max_size": 50,
        "total_size_bytes": 15420,
        "avg_access_time_ms": 0.234,
        "ttl_seconds": 3600,
        "persistence_enabled": true
      },
      "analysis_cache": {
        "hits": 89,
        "misses": 23,
        "hit_ratio": 79.46,
        "current_size": 23,
        "max_size": 100
      }
    },
    "cache_features": {
      "ttl_support": true,
      "persistence_support": true,
      "tag_invalidation": true,
      "multiple_instances": true,
      "thread_safe": true,
      "lru_eviction": true
    },
    "configuration": {
      "default_ttl_seconds": 3600,
      "persistence_enabled": false,
      "persistence_path": "/tmp/osp_cache/cache.json"
    }
  }
}
```

### `cleanup_expired_cache`

Manually cleanup expired cache entries across all cache instances.

**Signature:**

```python
async def cleanup_expired_cache() -> Dict[str, Any]
```

**Returns:**

```json
{
  "success": true,
  "data": {
    "cleanup_results": {
      "default": 8,
      "analysis_cache": 3,
      "batch_cache": 0
    },
    "total_removed": 11,
    "cache_count": 3,
    "cleanup_timestamp": "2025-08-18T10:30:00Z"
  }
}
```

## Usage Examples (v0.3.0)

### Batch Processing

```python
import asyncio

async def process_blog_posts():
    # Prepare batch content
    content_items = [
        {
            "id": "post_1",
            "content": "Your first blog post content...",
            "frameworks": ["IDEAL", "STEPPS"],
            "metadata": {"category": "tech", "author": "john"},
            "priority": 5
        },
        {
            "id": "post_2",
            "content": "Your second blog post content...",
            "frameworks": ["E-E-A-T"],
            "priority": 3
        },
        "Simple string content for quick analysis"  # Will use default frameworks
    ]

    # Start batch processing
    result = await analyze_content_batch(
        batch_id="blog_analysis_2025",
        content_items=content_items,
        default_frameworks=["IDEAL", "STEPPS"],
        priority=0
    )

    if result["success"]:
        summary = result["data"]["summary"]
        print(f"Processed {summary['total_items']} items")
        print(f"Success rate: {summary['success_rate']}%")
        print(f"Total time: {summary['total_processing_time_seconds']}s")

        # Process individual results
        for item_result in result["data"]["results"]:
            if item_result["success"]:
                print(f"Item {item_result['item_id']}: Success")
                # Access analysis data
                analysis = item_result["data"]
            else:
                print(f"Item {item_result['item_id']}: Failed - {item_result['error']}")
    else:
        print(f"Batch failed: {result['error']}")

# Run batch analysis
asyncio.run(process_blog_posts())
```

### Monitoring Batch Operations

```python
async def monitor_batches():
    # Check active batches
    status = await get_batch_status()

    if status["success"]:
        data = status["data"]
        print(f"Active batches: {data['active_count']}")

        for batch_id in data["active_batches"]:
            print(f"- {batch_id} is processing...")

        # Show recent history
        for batch in data["recent_history"]:
            success_rate = batch["summary"]["success_rate"]
            print(f"Recent batch {batch['batch_id']}: {success_rate}% success")

# Monitor system
asyncio.run(monitor_batches())
```

### Advanced Cache Management

```python
async def cache_maintenance():
    # Get detailed cache information
    cache_info = await get_advanced_cache_info()

    if cache_info["success"]:
        stats = cache_info["data"]["cache_statistics"]

        for cache_name, cache_stats in stats.items():
            hit_ratio = cache_stats["hit_ratio"]
            current_size = cache_stats["current_size"]
            max_size = cache_stats["max_size"]

            print(f"Cache '{cache_name}':")
            print(f"  Hit ratio: {hit_ratio}%")
            print(f"  Usage: {current_size}/{max_size}")

            # Cleanup if hit ratio is low
            if hit_ratio < 50:
                print(f"  Low hit ratio, cleaning up...")
                cleanup_result = await cleanup_expired_cache()
                if cleanup_result["success"]:
                    removed = cleanup_result["data"]["total_removed"]
                    print(f"  Removed {removed} expired entries")

# Perform cache maintenance
asyncio.run(cache_maintenance())
```

---

**API Version**: 0.3.0 **Last Updated**: 2025-08-18 **Protocol**: Model Context
Protocol (MCP)
