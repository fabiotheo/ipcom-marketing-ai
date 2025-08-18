"""Batch processing system for OSP Marketing Tools v0.3.0."""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .analysis import analyze_content_with_frameworks
from .config import BatchProcessingConfig, Config, config_manager

logger = logging.getLogger(__name__)


@dataclass
class BatchItem:
    """Single item in a batch processing request."""

    id: str
    content: str
    frameworks: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher numbers = higher priority


@dataclass
class BatchResult:
    """Result of processing a single batch item."""

    item_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0
    framework_count: int = 0


@dataclass
class BatchProgress:
    """Progress tracking for batch operations."""

    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    current_item: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    estimated_completion_time: Optional[float] = None

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100

    @property
    def elapsed_time_seconds(self) -> float:
        """Calculate elapsed time in seconds."""
        return time.time() - self.start_time

    def update_estimated_completion(self) -> None:
        """Update estimated completion time based on current progress."""
        if self.completed_items > 0:
            avg_time_per_item = self.elapsed_time_seconds / self.completed_items
            remaining_items = self.total_items - self.completed_items
            self.estimated_completion_time = time.time() + (
                avg_time_per_item * remaining_items
            )


class BatchProcessor:
    """Advanced batch processing system for content analysis."""

    def __init__(self, config: Optional[BatchProcessingConfig] = None):
        self.config = config or config_manager.get_batch_config()
        self.progress_tracker: Optional[BatchProgress] = None
        self._cancellation_token = False

    async def process_batch(
        self,
        items: List[BatchItem],
        progress_callback: Optional[Callable[[BatchProgress], None]] = None,
    ) -> Dict[str, Any]:
        """Process a batch of content analysis requests."""

        # Validate batch size
        if len(items) > self.config.max_batch_size:
            raise ValueError(
                f"Batch size ({len(items)}) exceeds maximum allowed ({self.config.max_batch_size})"
            )

        if not items:
            return {
                "success": True,
                "results": [],
                "summary": self._create_summary([], 0),
            }

        # Initialize progress tracking
        self.progress_tracker = BatchProgress(total_items=len(items))
        self._cancellation_token = False

        logger.info(f"Starting batch processing of {len(items)} items")

        try:
            # Sort items by priority (higher priority first)
            sorted_items = sorted(items, key=lambda x: x.priority, reverse=True)

            # Process items in parallel batches
            results = await self._process_parallel(sorted_items, progress_callback)

            # Create summary
            summary = self._create_summary(
                results, self.progress_tracker.elapsed_time_seconds
            )

            logger.info(
                f"Batch processing completed. Success rate: {summary['success_rate']}%"
            )

            return {
                "success": True,
                "results": results,
                "summary": summary,
                "progress": {
                    "total_items": self.progress_tracker.total_items,
                    "completed_items": self.progress_tracker.completed_items,
                    "failed_items": self.progress_tracker.failed_items,
                    "processing_time_seconds": self.progress_tracker.elapsed_time_seconds,
                },
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            return {
                "success": False,
                "error": f"Batch processing failed: {str(e)}",
                "results": [],
                "summary": self._create_summary([], 0),
            }

    async def _process_parallel(
        self,
        items: List[BatchItem],
        progress_callback: Optional[Callable[[BatchProgress], None]],
    ) -> List[BatchResult]:
        """Process items in parallel using thread pool."""

        results = []
        semaphore = asyncio.Semaphore(self.config.parallel_workers)

        async def process_single_item(item: BatchItem) -> BatchResult:
            async with semaphore:
                if self._cancellation_token:
                    return BatchResult(
                        item_id=item.id, success=False, error="Processing cancelled"
                    )

                return await self._process_item(item)

        # Create tasks for all items explicitly
        tasks = [asyncio.create_task(process_single_item(item)) for item in items]

        # Process with timeout
        try:
            # Use asyncio.wait with timeout
            done, pending = await asyncio.wait(
                tasks,
                timeout=self.config.timeout_seconds,
                return_when=asyncio.ALL_COMPLETED,
            )

            # Cancel any pending tasks
            for task in pending:
                task.cancel()

            # Collect results
            for task in done:
                try:
                    result = await task
                    results.append(result)

                    # Update progress
                    if self.progress_tracker:
                        if result.success:
                            self.progress_tracker.completed_items += 1
                        else:
                            self.progress_tracker.failed_items += 1

                        self.progress_tracker.current_item = result.item_id
                        self.progress_tracker.update_estimated_completion()

                        # Call progress callback
                        if progress_callback:
                            progress_callback(self.progress_tracker)

                except Exception as e:
                    logger.error(f"Error collecting task result: {str(e)}")
                    results.append(
                        BatchResult(
                            item_id="unknown",
                            success=False,
                            error=f"Task collection error: {str(e)}",
                        )
                    )

            # Handle timeout cases
            if pending:
                logger.warning(
                    f"Batch processing timed out. {len(pending)} items incomplete."
                )
                for task in pending:
                    results.append(
                        BatchResult(
                            item_id="timeout", success=False, error="Processing timeout"
                        )
                    )

        except asyncio.TimeoutError:
            logger.error("Batch processing timed out")
            # Cancel all tasks
            for task in tasks:
                task.cancel()

        return results

    async def _process_item(self, item: BatchItem) -> BatchResult:
        """Process a single batch item."""
        start_time = time.time()

        try:
            # Use default frameworks if none specified
            frameworks = item.frameworks or ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

            # Validate content
            if not item.content or not item.content.strip():
                return BatchResult(
                    item_id=item.id,
                    success=False,
                    error="Empty or invalid content",
                    processing_time_ms=0,
                )

            # Run analysis
            analysis_result = analyze_content_with_frameworks(item.content, frameworks)

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            return BatchResult(
                item_id=item.id,
                success=True,
                data=analysis_result,
                processing_time_ms=processing_time_ms,
                framework_count=len(frameworks),
            )

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error processing item {item.id}: {str(e)}")

            return BatchResult(
                item_id=item.id,
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms,
            )

    def _create_summary(
        self, results: List[BatchResult], total_time_seconds: float
    ) -> Dict[str, Any]:
        """Create batch processing summary."""
        if not results:
            return {
                "total_items": 0,
                "successful_items": 0,
                "failed_items": 0,
                "success_rate": 0,
                "total_processing_time_seconds": total_time_seconds,
                "average_processing_time_ms": 0,
                "total_frameworks_processed": 0,
            }

        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        total_items = len(results)
        successful_items = len(successful_results)
        failed_items = len(failed_results)
        success_rate = (successful_items / total_items * 100) if total_items > 0 else 0

        # Calculate processing times
        processing_times = [
            r.processing_time_ms for r in results if r.processing_time_ms > 0
        ]
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        # Calculate total frameworks processed
        total_frameworks = sum(r.framework_count for r in successful_results)

        return {
            "total_items": total_items,
            "successful_items": successful_items,
            "failed_items": failed_items,
            "success_rate": round(success_rate, 2),
            "total_processing_time_seconds": round(total_time_seconds, 2),
            "average_processing_time_ms": round(avg_processing_time, 2),
            "total_frameworks_processed": total_frameworks,
            "throughput_items_per_second": (
                round(total_items / total_time_seconds, 2)
                if total_time_seconds > 0
                else 0
            ),
        }

    def cancel_processing(self) -> None:
        """Cancel ongoing batch processing."""
        self._cancellation_token = True
        logger.info("Batch processing cancellation requested")


class BatchAnalysisManager:
    """High-level manager for batch analysis operations."""

    def __init__(self):
        self.active_batches: Dict[str, BatchProcessor] = {}
        self.batch_history: List[Dict[str, Any]] = []

    async def submit_batch(
        self,
        batch_id: str,
        content_items: List[Dict[str, Any]],
        default_frameworks: Optional[List[str]] = None,
        priority: int = 0,
    ) -> Dict[str, Any]:
        """Submit a new batch for processing."""

        # Convert content items to BatchItem objects
        batch_items = []
        for i, item in enumerate(content_items):
            if isinstance(item, str):
                # Simple string content
                batch_item = BatchItem(
                    id=f"{batch_id}_item_{i}",
                    content=item,
                    frameworks=default_frameworks,
                    priority=priority,
                )
            elif isinstance(item, dict):
                # Structured content item
                batch_item = BatchItem(
                    id=item.get("id", f"{batch_id}_item_{i}"),
                    content=item.get("content", ""),
                    frameworks=item.get("frameworks", default_frameworks),
                    metadata=item.get("metadata", {}),
                    priority=item.get("priority", priority),
                )
            else:
                raise ValueError(f"Invalid content item type: {type(item)}")

            batch_items.append(batch_item)

        # Create processor
        processor = BatchProcessor()
        self.active_batches[batch_id] = processor

        try:
            # Process batch
            result = await processor.process_batch(batch_items)

            # Add to history
            self.batch_history.append(
                {
                    "batch_id": batch_id,
                    "timestamp": time.time(),
                    "summary": result.get("summary", {}),
                    "success": result.get("success", False),
                }
            )

            # Clean up
            del self.active_batches[batch_id]

            return result

        except Exception as e:
            # Clean up on error
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            raise e

    def get_active_batches(self) -> List[str]:
        """Get list of currently active batch IDs."""
        return list(self.active_batches.keys())

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel an active batch."""
        if batch_id in self.active_batches:
            self.active_batches[batch_id].cancel_processing()
            return True
        return False

    def get_batch_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent batch processing history."""
        return self.batch_history[-limit:] if self.batch_history else []


# Global batch manager instance
batch_manager = BatchAnalysisManager()
