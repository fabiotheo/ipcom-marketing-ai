# Developer Guide - OSP Marketing Tools

## Quick Start

### Prerequisites

- Python 3.10+ (< 3.14)
- Git
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/open-strategy-partners/osp-marketing-tools.git
cd osp-marketing-tools

# Install in development mode
pip install -e ".[dev]"

# Verify installation
pytest --version
black --version
```

### First Analysis

```python
from osp_marketing_tools.server import analyze_content_multi_framework

# Simple analysis
result = await analyze_content_multi_framework(
    content="Expert software development guide with practical examples.",
    frameworks=["IDEAL", "STEPPS"]
)

print(f"Success: {result['success']}")
print(f"Average Score: {result['data']['analysis']['overall_scores']['average_score']}")
```

## Development Workflow

### 1. Code Changes

```bash
# Create feature branch
git checkout -b feature/new-framework

# Make changes
# ... edit files ...

# Format code
black src/ tests/
```

### 2. Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_analysis.py -v

# Run with coverage
pytest --cov=src/osp_marketing_tools --cov-report=html

# Performance tests
pytest tests/performance/ -m performance --no-cov -s
```

### 3. Quality Checks

```bash
# Linting
flake8 src/ tests/

# Type checking
mypy src/

# All quality checks
black src/ tests/ && flake8 src/ tests/ && mypy src/ && pytest
```

### 4. Commit and Push

```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "feat: add new framework analyzer"

# Push to feature branch
git push origin feature/new-framework
```

## Adding New Features

### Adding a New Framework

1. **Create Analyzer Class**

```python
# src/osp_marketing_tools/analysis.py

class NewFrameworkAnalyzer(FrameworkAnalyzer):
    """Analyzer for New Framework."""

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using New Framework."""

        # Component 1 Analysis
        component1_score = self._analyze_component1(content)
        component1_recommendations = self._get_component1_recommendations(
            content, component1_score
        )

        # Component 2 Analysis
        component2_score = self._analyze_component2(content)
        component2_recommendations = self._get_component2_recommendations(
            content, component2_score
        )

        return {
            "component1": {
                "score": component1_score,
                "recommendations": component1_recommendations
            },
            "component2": {
                "score": component2_score,
                "recommendations": component2_recommendations
            }
        }

    def _analyze_component1(self, content: str) -> float:
        """Analyze component1 aspect."""
        # Implementation here
        keywords = ["example", "guide", "practical"]
        score = analyze_keyword_score(content, keywords)
        return calculate_score(score, max_score=100, threshold=3)

    def _get_component1_recommendations(self, content: str, score: float) -> str:
        """Generate recommendations for component1."""
        if score < 50:
            return "Consider adding more practical examples and guides."
        elif score < 80:
            return "Good foundation, enhance with specific use cases."
        else:
            return "Excellent component1 implementation."
```

2. **Register Framework**

```python
# Add to FRAMEWORK_ANALYZERS dictionary
FRAMEWORK_ANALYZERS["NEW_FRAMEWORK"] = NewFrameworkAnalyzer()
```

3. **Add Tests**

```python
# tests/unit/test_analysis.py

class TestNewFrameworkAnalyzer:
    """Test New Framework analyzer."""

    @pytest.fixture
    def analyzer(self):
        return NewFrameworkAnalyzer()

    def test_analyze_basic_content(self, analyzer):
        """Test basic content analysis."""
        content = "This is a practical guide with examples."
        result = analyzer.analyze(content)

        assert "component1" in result
        assert "component2" in result
        assert isinstance(result["component1"]["score"], (int, float))
        assert 0 <= result["component1"]["score"] <= 100

    def test_analyze_empty_content(self, analyzer):
        """Test empty content handling."""
        result = analyzer.analyze("")

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_recommendations_quality(self, analyzer):
        """Test recommendation quality."""
        content = "Expert development guide with comprehensive examples."
        result = analyzer.analyze(content)

        for component in result.values():
            assert len(component["recommendations"]) > 10
            assert not component["recommendations"].startswith("Error")
```

4. **Integration Tests**

```python
# tests/integration/test_basic_integration.py

@pytest.mark.asyncio
async def test_new_framework_integration():
    """Test new framework integration."""
    content = "Test content for new framework validation."

    result = await analyze_content_multi_framework(content, ["NEW_FRAMEWORK"])

    assert result["success"] is True
    assert "NEW_FRAMEWORK" in result["data"]["analysis"]["frameworks"]

    framework_result = result["data"]["analysis"]["frameworks"]["NEW_FRAMEWORK"]
    assert "component1" in framework_result
    assert "component2" in framework_result
```

### Adding MCP Tools

1. **Define Tool Function**

```python
# src/osp_marketing_tools/server.py

@mcp.tool()
@handle_exceptions
async def new_tool_function(parameter1: str, parameter2: int = 10) -> Dict[str, Any]:
    """New MCP tool for specific functionality.

    Args:
        parameter1: Description of parameter 1
        parameter2: Description of parameter 2 (default: 10)

    Returns:
        Dictionary with tool results
    """
    logger.info(f"Executing new tool with params: {parameter1}, {parameter2}")

    try:
        # Tool implementation
        result = perform_tool_operation(parameter1, parameter2)

        return {
            "success": True,
            "result": result,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "0.3.0"
            }
        }

    except Exception as e:
        logger.error(f"Error in new tool: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

2. **Add Tool Tests**

```python
# tests/unit/test_mcp_functions.py

class TestNewToolFunction:
    """Test new MCP tool function."""

    @pytest.mark.asyncio
    async def test_new_tool_success(self):
        """Test successful tool execution."""
        result = await new_tool_function("test_param", 20)

        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_new_tool_error_handling(self):
        """Test tool error handling."""
        result = await new_tool_function("", -1)  # Invalid params

        assert result["success"] is False
        assert "error" in result
```

## Testing Strategies

### Unit Tests

**Scope**: Individual functions and classes **Location**: `tests/unit/`
**Coverage Target**: 100% for business logic

```python
# Example unit test
def test_calculate_score():
    """Test score calculation utility."""
    # Test normal case
    score = calculate_score(75, max_score=100, threshold=5)
    assert score == 75.0

    # Test edge cases
    assert calculate_score(0, 100, 5) == 0.0
    assert calculate_score(150, 100, 5) == 100.0
```

### Integration Tests

**Scope**: Component interactions **Location**: `tests/integration/` **Focus**:
End-to-end workflows

```python
# Example integration test
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_analysis_workflow():
    """Test complete analysis workflow."""
    content = "Comprehensive guide for testing purposes."

    # Test full pipeline
    result = await analyze_content_multi_framework(content, ["IDEAL", "STEPPS"])

    # Verify structure
    assert result["success"] is True
    assert len(result["data"]["analysis"]["frameworks"]) == 2

    # Verify metadata
    assert "processing_time_ms" in result["metadata"]
    assert result["metadata"]["total_frameworks"] == 2
```

### Performance Tests

**Scope**: Performance benchmarks **Location**: `tests/performance/` **Focus**:
Speed and resource usage

```python
# Example performance test
@pytest.mark.performance
@pytest.mark.asyncio
async def test_analysis_performance():
    """Test analysis performance."""
    content = "Content for performance testing." * 100

    start_time = time.perf_counter()
    result = await analyze_content_multi_framework(content, ["IDEAL"])
    end_time = time.perf_counter()

    processing_time = (end_time - start_time) * 1000  # ms

    assert result["success"] is True
    assert processing_time < 1000  # Should complete under 1 second
```

## Code Quality Standards

### Code Style

```python
# Good: Clear, typed function
async def analyze_framework_content(
    content: str,
    framework: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Analyze content using specified framework.

    Args:
        content: Text content to analyze
        framework: Framework name (IDEAL, STEPPS, etc.)
        options: Optional analysis parameters

    Returns:
        Analysis results with scores and recommendations

    Raises:
        ContentValidationError: If content is invalid
        FrameworkValidationError: If framework is not supported
    """
    if not content.strip():
        raise ContentValidationError("Content cannot be empty")

    analyzer = FRAMEWORK_ANALYZERS.get(framework)
    if not analyzer:
        raise FrameworkValidationError(f"Framework '{framework}' not supported")

    return analyzer.analyze(content)

# Bad: Unclear, untyped function
def analyze(c, f, o=None):
    if not c:
        raise Exception("bad content")
    return FRAMEWORK_ANALYZERS[f].analyze(c)
```

### Error Handling

```python
# Good: Specific exceptions with context
class ContentValidationError(Exception):
    """Raised when content validation fails."""
    pass

def validate_content(content: str) -> None:
    """Validate content for analysis."""
    if not content or not content.strip():
        raise ContentValidationError("Content parameter is required")

    if len(content) > Config.MAX_ANALYSIS_CONTENT_LENGTH:
        raise ContentValidationError(
            f"Content too long: {len(content)} characters "
            f"(max: {Config.MAX_ANALYSIS_CONTENT_LENGTH})"
        )

# Bad: Generic exceptions
def validate_content(content):
    if not content:
        raise Exception("bad content")
```

### Documentation

```python
# Good: Comprehensive docstring
def calculate_score(
    raw_score: float,
    max_score: float = 100.0,
    threshold: float = 1.0
) -> float:
    """Calculate normalized score with threshold.

    Normalizes a raw score to a 0-100 scale with configurable thresholds.
    Scores below threshold are set to 0, scores above max_score are capped.

    Args:
        raw_score: Raw calculated score
        max_score: Maximum possible score (default: 100.0)
        threshold: Minimum threshold for non-zero score (default: 1.0)

    Returns:
        Normalized score between 0 and 100

    Example:
        >>> calculate_score(75.5, max_score=100, threshold=5)
        75.5
        >>> calculate_score(2.0, max_score=100, threshold=5)
        0.0
    """
    if raw_score < threshold:
        return 0.0

    return min(raw_score, max_score)

# Bad: No documentation
def calc(s, m=100, t=1):
    return min(s, m) if s >= t else 0
```

## Debugging

### Logging Configuration

```python
# Enable debug logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Framework-specific logging
logger = logging.getLogger('osp_marketing_tools.analysis')
logger.setLevel(logging.DEBUG)
```

### Common Debug Patterns

```python
# Debug function entry/exit
def analyze_content(content: str) -> Dict[str, Any]:
    logger.debug(f"Starting analysis for content length: {len(content)}")

    try:
        result = perform_analysis(content)
        logger.debug(f"Analysis completed successfully: {len(result)} components")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

# Debug performance
import time

def timed_operation():
    start_time = time.perf_counter()
    try:
        result = expensive_operation()
        return result
    finally:
        end_time = time.perf_counter()
        logger.debug(f"Operation took {(end_time - start_time) * 1000:.2f}ms")
```

### Testing Debug Mode

```bash
# Run tests with debug output
pytest -v -s --log-cli-level=DEBUG

# Test specific function with debugging
pytest tests/unit/test_analysis.py::test_specific_function -v -s --pdb
```

## Performance Optimization

### Profiling

```python
# Profile function performance
import cProfile
import pstats

def profile_analysis():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run analysis
    result = analyze_content_multi_framework(content, frameworks)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
```

### Memory Optimization

```python
# Monitor memory usage
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    logger.info(f"Memory usage: {memory_mb:.2f} MB")
```

### Async Best Practices

```python
# Good: Proper async/await usage
async def analyze_multiple_contents(contents: List[str]) -> List[Dict[str, Any]]:
    """Analyze multiple contents concurrently."""
    tasks = [
        analyze_content_multi_framework(content, ["IDEAL"])
        for content in contents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions in results
    successful_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Analysis failed: {result}")
        else:
            successful_results.append(result)

    return successful_results

# Bad: Blocking in async function
async def analyze_multiple_contents_bad(contents):
    results = []
    for content in contents:
        result = analyze_content_multi_framework(content, ["IDEAL"])  # Missing await
        results.append(result)
    return results
```

## Deployment Preparation

### Environment Setup

```bash
# Production dependencies only
pip install -e .

# Set production environment variables
export OSP_LOG_LEVEL=INFO
export OSP_CACHE_SIZE=100
export OSP_MAX_FILE_SIZE_MB=50
```

### Health Checks

```python
# Implement health check endpoint
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health check for monitoring."""
    try:
        # Test framework loading
        frameworks = list(FRAMEWORK_ANALYZERS.keys())

        # Test basic analysis
        test_result = await analyze_content_multi_framework(
            "Health check test content for system validation.",
            ["IDEAL"]
        )

        return {
            "success": True,
            "status": "healthy",
            "frameworks_available": frameworks,
            "test_analysis_success": test_result["success"],
            "version": "0.3.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

## Batch Processing System (v0.3.0)

### Overview

The batch processing system allows efficient parallel analysis of multiple
content items with advanced features:

- **Concurrent Processing**: Configurable parallel workers (default: 4)
- **Priority Queue**: Higher priority items processed first
- **Progress Tracking**: Real-time monitoring of batch progress
- **Error Handling**: Individual item failures don't stop the batch
- **Cancellation**: Active batches can be cancelled
- **History**: Recent batch history tracking

### Architecture

```
BatchAnalysisManager
├── BatchProcessor (per batch)
│   ├── BatchProgress (tracking)
│   ├── Semaphore (concurrency control)
│   └── asyncio.create_task() (parallel execution)
└── BatchResult[] (results collection)
```

### Configuration

```python
# Environment variables for batch processing
OSP_BATCH_MAX_SIZE=10      # Maximum items per batch
OSP_BATCH_WORKERS=4        # Parallel workers
OSP_BATCH_TIMEOUT=300      # Timeout in seconds (5 minutes)
```

### Development Examples

#### Basic Batch Implementation

```python
from osp_marketing_tools.batch import batch_manager, BatchItem

async def process_content_batch():
    """Example of using the batch system directly."""

    # Create batch items
    items = [
        BatchItem(
            id="item_1",
            content="First content to analyze...",
            frameworks=["IDEAL", "STEPPS"],
            metadata={"source": "blog"},
            priority=5
        ),
        BatchItem(
            id="item_2",
            content="Second content to analyze...",
            frameworks=["E-E-A-T"],
            priority=3
        )
    ]

    # Submit for processing
    result = await batch_manager.submit_batch(
        batch_id="dev_test_batch",
        content_items=[item.__dict__ for item in items]
    )

    return result
```

#### Testing Batch Operations

```python
# tests/unit/test_batch_custom.py

import pytest
from unittest.mock import patch
from osp_marketing_tools.batch import BatchProcessor, BatchItem

@pytest.mark.asyncio
async def test_batch_processor_custom():
    """Test custom batch processing logic."""
    processor = BatchProcessor()

    # Mock the analysis function
    mock_result = {"frameworks": {"IDEAL": {"score": 85}}}

    with patch("osp_marketing_tools.batch.analyze_content_with_frameworks", return_value=mock_result):
        items = [
            BatchItem(id="test_1", content="Test content", frameworks=["IDEAL"]),
            BatchItem(id="test_2", content="Test content 2", frameworks=["STEPPS"])
        ]

        result = await processor.process_batch(items)

        assert result["success"] is True
        assert len(result["results"]) == 2
        assert result["summary"]["total_items"] == 2
```

#### Performance Monitoring

```python
from osp_marketing_tools.batch import batch_manager

async def monitor_batch_performance():
    """Monitor batch system performance."""

    # Get active batches
    active_batches = batch_manager.get_active_batches()
    print(f"Active batches: {len(active_batches)}")

    # Get recent history with performance metrics
    history = batch_manager.get_batch_history(limit=10)

    for batch in history:
        summary = batch["summary"]
        throughput = summary.get("throughput_items_per_second", 0)
        success_rate = summary.get("success_rate", 0)

        print(f"Batch {batch['batch_id']}:")
        print(f"  Throughput: {throughput:.2f} items/sec")
        print(f"  Success rate: {success_rate:.1f}%")
```

### Advanced Cache System (v0.3.0)

The advanced cache system provides enterprise-grade features:

#### Key Features

- **TTL Support**: Time-based expiration (configurable)
- **Persistence**: Optional disk-based persistence
- **Tag Invalidation**: Invalidate related cache entries
- **Multiple Instances**: Named cache instances
- **LRU Eviction**: Automatic memory management
- **Thread Safety**: Concurrent access protection
- **Metrics**: Detailed performance statistics

#### Development Usage

```python
from osp_marketing_tools.cache import cache_manager, AdvancedLRUCache

# Using global cache manager
cache = cache_manager.get_cache("analysis_cache")
cache.put("content_hash_123", analysis_result, tags=["IDEAL", "batch_001"])

# Creating custom cache with specific config
custom_cache = AdvancedLRUCache(
    max_size=100,
    ttl_seconds=1800,  # 30 minutes
    enable_persistence=True,
    persistence_path="/tmp/my_cache.json"
)

# Tag-based invalidation
cache.invalidate_by_tags(["batch_001"])  # Remove all batch_001 results

# Performance monitoring
stats = cache.get_stats()
print(f"Hit ratio: {stats['hit_ratio']:.1f}%")
print(f"Cache size: {stats['current_size']}/{stats['max_size']}")
```

#### Testing Cache Features

```python
# tests/unit/test_cache_custom.py

def test_cache_ttl_expiration():
    """Test TTL-based cache expiration."""
    cache = AdvancedLRUCache(max_size=10, ttl_seconds=0.1)

    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"

    time.sleep(0.15)  # Wait for expiration
    assert cache.get("key1") is None

    stats = cache.get_stats()
    assert stats["expired_removals"] == 1
```

## Contributing Guidelines

### Pull Request Process

1. **Fork** repository
2. **Create** feature branch: `git checkout -b feature/description`
3. **Implement** changes with tests
4. **Run** quality checks: `black`, `flake8`, `mypy`, `pytest`
5. **Update** documentation if needed
6. **Submit** PR with clear description

### Code Review Checklist

- [ ] Code follows style guidelines (Black, Flake8)
- [ ] All tests pass
- [ ] Coverage maintained/improved
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Performance impact considered
- [ ] Error handling appropriate
- [ ] Security implications reviewed

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:

```
feat(analysis): add new sentiment analysis framework
fix(server): handle edge case in content validation
docs(api): update framework analysis documentation
test(performance): add memory usage benchmarks
```

---

**Happy Coding!** 🚀
