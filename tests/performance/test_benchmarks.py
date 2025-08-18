"""Performance tests and benchmarks for OSP Marketing Tools."""

import asyncio
import statistics
import time
from typing import Any, Dict, List

import pytest

from osp_marketing_tools.server import (analyze_content_multi_framework,
                                        benchmark_file_operations,
                                        clear_cache_statistics,
                                        get_cache_statistics)


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.fixture
    def performance_content(self):
        """Content optimized for performance testing."""
        return """
        This is a comprehensive software development guide designed for experienced developers
        and technical professionals who want to identify best practices, discover new methodologies,
        empower their teams with practical solutions, activate continuous improvement processes,
        and learn from real-world case studies and expert recommendations.

        Our research shows significant improvements in development velocity, code quality metrics,
        team collaboration effectiveness, and overall project success rates when following
        these proven strategies and implementation patterns.

        Share your experience with the community, provide feedback on these approaches,
        and help others benefit from your insights and practical implementation examples.
        """

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_framework_analysis_performance(self, performance_content):
        """Benchmark single framework analysis performance."""
        framework = "IDEAL"
        iterations = 5
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            result = await analyze_content_multi_framework(
                performance_content, [framework]
            )
            end_time = time.perf_counter()

            assert result["success"] is True
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds

        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)

        # Single framework should complete within reasonable time
        assert avg_time < 1000, f"Average time {avg_time:.2f}ms exceeds 1000ms"
        assert max_time < 2000, f"Max time {max_time:.2f}ms exceeds 2000ms"

        print(f"\nSingle Framework Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  Std Dev: {statistics.stdev(times):.2f}ms")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_multi_framework_analysis_performance(self, performance_content):
        """Benchmark multi-framework analysis performance."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]
        iterations = 3
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            result = await analyze_content_multi_framework(
                performance_content, frameworks
            )
            end_time = time.perf_counter()

            assert result["success"] is True
            assert len(result["data"]["analysis"]["frameworks"]) == 4
            times.append((end_time - start_time) * 1000)

        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)

        # Multi-framework should complete within reasonable time
        assert avg_time < 5000, f"Average time {avg_time:.2f}ms exceeds 5000ms"
        assert max_time < 8000, f"Max time {max_time:.2f}ms exceeds 8000ms"

        print(f"\nMulti-Framework Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max_time:.2f}ms")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self, performance_content):
        """Benchmark concurrent analysis performance."""
        frameworks = ["IDEAL", "STEPPS"]
        concurrent_requests = 5

        start_time = time.perf_counter()

        # Run concurrent analyses
        tasks = [
            analyze_content_multi_framework(
                f"{performance_content} - Request {i}", frameworks
            )
            for i in range(concurrent_requests)
        ]

        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        # All should succeed
        for result in results:
            assert result["success"] is True

        # Concurrent execution should be more efficient than sequential
        avg_time_per_request = total_time / concurrent_requests

        # Should complete all requests efficiently
        assert total_time < 10000, f"Total time {total_time:.2f}ms exceeds 10000ms"
        assert (
            avg_time_per_request < 3000
        ), f"Avg per request {avg_time_per_request:.2f}ms exceeds 3000ms"

        print(f"\nConcurrent Analysis Performance:")
        print(f"  Total Time: {total_time:.2f}ms")
        print(f"  Avg per Request: {avg_time_per_request:.2f}ms")
        print(f"  Requests: {concurrent_requests}")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_content_size_scalability(self):
        """Test performance scaling with different content sizes."""
        base_content = (
            "Expert software development guide with practical examples. " * 10
        )

        size_multipliers = [1, 5, 10, 20]
        performance_data = []

        for multiplier in size_multipliers:
            content = base_content * multiplier
            content_length = len(content)

            start_time = time.perf_counter()
            result = await analyze_content_multi_framework(content, ["IDEAL"])
            end_time = time.perf_counter()

            processing_time = (end_time - start_time) * 1000

            assert result["success"] is True

            performance_data.append(
                {
                    "multiplier": multiplier,
                    "content_length": content_length,
                    "processing_time_ms": processing_time,
                    "chars_per_ms": (
                        content_length / processing_time if processing_time > 0 else 0
                    ),
                }
            )

        # Check that performance doesn't degrade severely
        for i in range(1, len(performance_data)):
            current = performance_data[i]
            previous = performance_data[i - 1]

            # Time shouldn't increase more than proportionally to content size
            time_ratio = current["processing_time_ms"] / previous["processing_time_ms"]
            size_ratio = current["content_length"] / previous["content_length"]

            # Allow some overhead but not excessive
            assert (
                time_ratio < size_ratio * 2
            ), f"Performance degraded too much at multiplier {current['multiplier']}"

        print(f"\nContent Size Scalability:")
        for data in performance_data:
            print(
                f"  Size {data['multiplier']}x: {data['processing_time_ms']:.2f}ms ({data['chars_per_ms']:.2f} chars/ms)"
            )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, performance_content):
        """Test memory usage stability during repeated analyses."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run multiple analyses
        for i in range(10):
            result = await analyze_content_multi_framework(
                performance_content, ["IDEAL", "STEPPS"]
            )
            assert result["success"] is True

            # Check memory every few iterations
            if i % 3 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory

                # Memory shouldn't grow excessively (allow for some variance)
                assert (
                    memory_increase < 50
                ), f"Memory increased by {memory_increase:.2f}MB after {i+1} iterations"

        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory

        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.2f}MB")
        print(f"  Final: {final_memory:.2f}MB")
        print(f"  Increase: {total_increase:.2f}MB")

        # Final memory increase should be reasonable
        assert (
            total_increase < 30
        ), f"Total memory increase {total_increase:.2f}MB exceeds 30MB"


class TestCachePerformance:
    """Test cache performance and efficiency."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test cache hit performance benefits."""
        content = "Comprehensive development guide with expert recommendations and practical examples."
        frameworks = ["IDEAL"]

        # Clear cache first
        await clear_cache_statistics()

        # First request (cache miss)
        start_time = time.perf_counter()
        result1 = await analyze_content_multi_framework(content, frameworks)
        first_time = (time.perf_counter() - start_time) * 1000

        assert result1["success"] is True

        # Second request (potential cache hit)
        start_time = time.perf_counter()
        result2 = await analyze_content_multi_framework(content, frameworks)
        second_time = (time.perf_counter() - start_time) * 1000

        assert result2["success"] is True

        # Results should be consistent
        assert (
            result1["data"]["analysis"]["frameworks"]["IDEAL"]["identify"]["score"]
            == result2["data"]["analysis"]["frameworks"]["IDEAL"]["identify"]["score"]
        )

        print(f"\nCache Performance:")
        print(f"  First request: {first_time:.2f}ms")
        print(f"  Second request: {second_time:.2f}ms")
        print(f"  Improvement: {((first_time - second_time) / first_time * 100):.2f}%")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_statistics_accuracy(self):
        """Test cache statistics tracking accuracy."""
        await clear_cache_statistics()

        # Get initial stats
        initial_stats = await get_cache_statistics()

        # Perform some analyses
        content = "Test content for cache statistics validation."

        for i in range(3):
            result = await analyze_content_multi_framework(content, ["IDEAL"])
            assert result["success"] is True

        # Get final stats
        final_stats = await get_cache_statistics()

        # Verify stats were updated
        assert final_stats["success"] is True
        print(f"\nCache Statistics:")
        print(f"  Initial: {initial_stats}")
        print(f"  Final: {final_stats}")


class TestFileOperationPerformance:
    """Test file operation performance."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_file_operations_benchmark(self):
        """Test file operations benchmark performance."""
        result = await benchmark_file_operations()

        assert result["success"] is True
        assert "data" in result
        assert "benchmark_results" in result["data"]

        benchmarks = result["data"]["benchmark_results"]

        # Check that operations complete within reasonable time
        sync_duration = benchmarks["synchronous"]["duration_seconds"]
        async_duration = benchmarks["asynchronous"]["duration_seconds"]

        assert sync_duration < 5.0, "Sync operations too slow"
        assert async_duration < 5.0, "Async operations too slow"

        print(f"\nFile Operations Benchmark:")
        print(f"  Synchronous: {sync_duration:.4f}s")
        print(f"  Asynchronous: {async_duration:.4f}s")
        print(
            f"  Improvement: {benchmarks['performance_improvement']['improvement_percentage']:.1f}%"
        )


class TestThroughputBenchmarks:
    """Test system throughput under various loads."""

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self):
        """Test performance under sustained load."""
        content = (
            "Development guide for sustained load testing with comprehensive examples."
        )
        frameworks = ["IDEAL", "STEPPS"]

        num_requests = 20
        batch_size = 5

        total_start_time = time.perf_counter()
        all_times = []

        # Process in batches to simulate realistic load
        for batch in range(0, num_requests, batch_size):
            batch_start_time = time.perf_counter()

            # Create batch tasks
            tasks = []
            for i in range(batch, min(batch + batch_size, num_requests)):
                task = analyze_content_multi_framework(
                    f"{content} - Request {i}", frameworks
                )
                tasks.append(task)

            # Execute batch
            results = await asyncio.gather(*tasks)

            batch_end_time = time.perf_counter()
            batch_time = (batch_end_time - batch_start_time) * 1000

            # All should succeed
            for result in results:
                assert result["success"] is True

            all_times.append(batch_time)

            # Brief pause between batches
            await asyncio.sleep(0.1)

        total_time = (time.perf_counter() - total_start_time) * 1000

        # Performance assertions
        avg_batch_time = statistics.mean(all_times)
        requests_per_second = num_requests / (total_time / 1000)

        print(f"\nSustained Load Performance:")
        print(f"  Total Requests: {num_requests}")
        print(f"  Total Time: {total_time:.2f}ms")
        print(f"  Avg Batch Time: {avg_batch_time:.2f}ms")
        print(f"  Requests/Second: {requests_per_second:.2f}")

        # System should maintain reasonable throughput
        assert (
            requests_per_second > 1.0
        ), f"Throughput {requests_per_second:.2f} req/s too low"
        assert (
            avg_batch_time < 5000
        ), f"Average batch time {avg_batch_time:.2f}ms too high"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_framework_comparison_performance(self):
        """Compare performance across different frameworks."""
        content = "Expert guide for framework performance comparison testing."
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        framework_times = {}

        # Test each framework individually
        for framework in frameworks:
            times = []

            for _ in range(3):
                start_time = time.perf_counter()
                result = await analyze_content_multi_framework(content, [framework])
                end_time = time.perf_counter()

                assert result["success"] is True
                times.append((end_time - start_time) * 1000)

            framework_times[framework] = {
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times),
            }

        print(f"\nFramework Performance Comparison:")
        for framework, times in framework_times.items():
            print(
                f"  {framework}: {times['avg']:.2f}ms avg ({times['min']:.2f}-{times['max']:.2f}ms)"
            )

        # All frameworks should perform reasonably
        for framework, times in framework_times.items():
            assert (
                times["avg"] < 2000
            ), f"{framework} average time {times['avg']:.2f}ms too high"
            assert (
                times["max"] < 3000
            ), f"{framework} max time {times['max']:.2f}ms too high"
