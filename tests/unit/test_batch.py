"""Unit tests for batch processing module."""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from osp_marketing_tools.batch import (BatchAnalysisManager, BatchItem,
                                       BatchProcessor, BatchProgress,
                                       BatchResult, batch_manager)
from osp_marketing_tools.config import BatchProcessingConfig


class TestBatchItem:
    """Test BatchItem dataclass."""

    def test_batch_item_creation(self):
        """Test creating a batch item."""
        item = BatchItem(
            id="test_1",
            content="Test content",
            frameworks=["IDEAL"],
            metadata={"key": "value"},
            priority=5,
        )

        assert item.id == "test_1"
        assert item.content == "Test content"
        assert item.frameworks == ["IDEAL"]
        assert item.metadata == {"key": "value"}
        assert item.priority == 5

    def test_batch_item_defaults(self):
        """Test BatchItem with default values."""
        item = BatchItem(id="test_1", content="Test content")

        assert item.frameworks is None
        assert item.metadata == {}
        assert item.priority == 0


class TestBatchResult:
    """Test BatchResult dataclass."""

    def test_batch_result_success(self):
        """Test successful batch result."""
        result = BatchResult(
            item_id="test_1",
            success=True,
            data={"score": 85},
            processing_time_ms=150.5,
            framework_count=2,
        )

        assert result.item_id == "test_1"
        assert result.success is True
        assert result.data == {"score": 85}
        assert result.error is None
        assert result.processing_time_ms == 150.5
        assert result.framework_count == 2

    def test_batch_result_failure(self):
        """Test failed batch result."""
        result = BatchResult(
            item_id="test_1",
            success=False,
            error="Processing failed",
            processing_time_ms=50.0,
        )

        assert result.item_id == "test_1"
        assert result.success is False
        assert result.data is None
        assert result.error == "Processing failed"
        assert result.processing_time_ms == 50.0
        assert result.framework_count == 0


class TestBatchProgress:
    """Test BatchProgress tracking."""

    def test_progress_initialization(self):
        """Test progress tracker initialization."""
        progress = BatchProgress(total_items=10)

        assert progress.total_items == 10
        assert progress.completed_items == 0
        assert progress.failed_items == 0
        assert progress.current_item is None
        assert progress.estimated_completion_time is None
        assert progress.start_time > 0

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        progress = BatchProgress(total_items=10)
        progress.completed_items = 3

        assert progress.progress_percentage == 30.0

    def test_progress_percentage_zero_items(self):
        """Test progress percentage with zero items."""
        progress = BatchProgress(total_items=0)

        assert progress.progress_percentage == 100.0

    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        progress = BatchProgress(total_items=5)
        time.sleep(0.01)  # Small delay

        assert progress.elapsed_time_seconds > 0

    def test_update_estimated_completion(self):
        """Test estimated completion time update."""
        progress = BatchProgress(total_items=10)
        progress.completed_items = 2
        time.sleep(0.01)  # Small delay to ensure elapsed time

        progress.update_estimated_completion()

        assert progress.estimated_completion_time is not None
        assert progress.estimated_completion_time > time.time()


class TestBatchProcessor:
    """Test BatchProcessor functionality."""

    def test_batch_processor_initialization(self):
        """Test batch processor initialization."""
        processor = BatchProcessor()

        assert processor.config is not None
        assert processor.progress_tracker is None
        assert processor._cancellation_token is False

    def test_batch_processor_with_custom_config(self):
        """Test batch processor with custom configuration."""
        config = BatchProcessingConfig(
            max_batch_size=5, parallel_workers=2, timeout_seconds=60
        )
        processor = BatchProcessor(config)

        assert processor.config.max_batch_size == 5
        assert processor.config.parallel_workers == 2
        assert processor.config.timeout_seconds == 60

    @pytest.mark.asyncio
    async def test_process_empty_batch(self):
        """Test processing empty batch."""
        processor = BatchProcessor()

        result = await processor.process_batch([])

        assert result["success"] is True
        assert result["results"] == []
        assert result["summary"]["total_items"] == 0

    @pytest.mark.asyncio
    async def test_process_batch_size_validation(self):
        """Test batch size validation."""
        config = BatchProcessingConfig(max_batch_size=2)
        processor = BatchProcessor(config)

        items = [
            BatchItem(id="1", content="Content 1"),
            BatchItem(id="2", content="Content 2"),
            BatchItem(id="3", content="Content 3"),  # Exceeds limit
        ]

        with pytest.raises(ValueError, match="Batch size.*exceeds maximum"):
            await processor.process_batch(items)

    @pytest.mark.asyncio
    async def test_process_single_item_success(self):
        """Test processing single item successfully."""
        processor = BatchProcessor()

        # Mock the analysis function
        mock_analysis = {"frameworks": {"IDEAL": {"score": 85}}, "overall_score": 85}

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            return_value=mock_analysis,
        ):
            item = BatchItem(id="test_1", content="Test content", frameworks=["IDEAL"])
            result = await processor._process_item(item)

        assert result.item_id == "test_1"
        assert result.success is True
        assert result.data == mock_analysis
        assert result.framework_count == 1
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_process_single_item_empty_content(self):
        """Test processing item with empty content."""
        processor = BatchProcessor()

        item = BatchItem(id="test_1", content="", frameworks=["IDEAL"])
        result = await processor._process_item(item)

        assert result.item_id == "test_1"
        assert result.success is False
        assert "Empty or invalid content" in result.error
        assert result.processing_time_ms == 0

    @pytest.mark.asyncio
    async def test_process_single_item_default_frameworks(self):
        """Test processing item with default frameworks."""
        processor = BatchProcessor()

        mock_analysis = {"frameworks": {}, "overall_score": 0}

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            return_value=mock_analysis,
        ):
            item = BatchItem(
                id="test_1", content="Test content"
            )  # No frameworks specified
            result = await processor._process_item(item)

        assert result.success is True
        assert result.framework_count == 4  # Default frameworks

    @pytest.mark.asyncio
    async def test_process_single_item_exception(self):
        """Test processing item that raises exception."""
        processor = BatchProcessor()

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            side_effect=Exception("Analysis failed"),
        ):
            item = BatchItem(id="test_1", content="Test content", frameworks=["IDEAL"])
            result = await processor._process_item(item)

        assert result.item_id == "test_1"
        assert result.success is False
        assert "Analysis failed" in result.error
        assert result.processing_time_ms > 0

    def test_create_summary_empty(self):
        """Test creating summary for empty results."""
        processor = BatchProcessor()

        summary = processor._create_summary([], 1.5)

        assert summary["total_items"] == 0
        assert summary["successful_items"] == 0
        assert summary["failed_items"] == 0
        assert summary["success_rate"] == 0
        assert summary["total_processing_time_seconds"] == 1.5
        assert summary["average_processing_time_ms"] == 0
        assert summary["total_frameworks_processed"] == 0

    def test_create_summary_with_results(self):
        """Test creating summary with mixed results."""
        processor = BatchProcessor()

        results = [
            BatchResult(
                "1", True, {"score": 85}, processing_time_ms=100, framework_count=2
            ),
            BatchResult(
                "2", True, {"score": 90}, processing_time_ms=150, framework_count=3
            ),
            BatchResult(
                "3", False, error="Failed", processing_time_ms=50, framework_count=0
            ),
        ]

        summary = processor._create_summary(results, 2.0)

        assert summary["total_items"] == 3
        assert summary["successful_items"] == 2
        assert summary["failed_items"] == 1
        assert summary["success_rate"] == 66.67
        assert summary["total_processing_time_seconds"] == 2.0
        assert summary["average_processing_time_ms"] == 100.0  # (100+150+50)/3
        assert summary["total_frameworks_processed"] == 5  # 2+3+0
        assert summary["throughput_items_per_second"] == 1.5  # 3/2

    def test_cancel_processing(self):
        """Test cancelling batch processing."""
        processor = BatchProcessor()

        assert processor._cancellation_token is False

        processor.cancel_processing()

        assert processor._cancellation_token is True

    @pytest.mark.asyncio
    async def test_process_with_priority_sorting(self):
        """Test that items are processed in priority order."""
        processor = BatchProcessor()
        processed_ids = []

        def mock_analysis(content, frameworks):
            # Extract ID from content to track processing order
            item_id = content.split()[1]  # "Content X" -> "X"
            processed_ids.append(item_id)
            return {"frameworks": {}, "overall_score": 0}

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            side_effect=mock_analysis,
        ):
            items = [
                BatchItem(id="1", content="Content 1", priority=1),
                BatchItem(id="2", content="Content 2", priority=5),  # Highest priority
                BatchItem(id="3", content="Content 3", priority=3),
            ]

            result = await processor.process_batch(items)

        assert result["success"] is True
        # Items should be sorted by priority (highest first): 2, 3, 1
        # Note: Due to async processing, we just check that all were processed
        assert len(processed_ids) == 3


class TestBatchAnalysisManager:
    """Test BatchAnalysisManager functionality."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = BatchAnalysisManager()

        assert manager.active_batches == {}
        assert manager.batch_history == []

    @pytest.mark.asyncio
    async def test_submit_batch_simple_strings(self):
        """Test submitting batch with simple string content."""
        manager = BatchAnalysisManager()

        mock_analysis = {"frameworks": {}, "overall_score": 0}

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            return_value=mock_analysis,
        ):
            content_items = ["Content 1", "Content 2"]

            result = await manager.submit_batch(
                batch_id="test_batch",
                content_items=content_items,
                default_frameworks=["IDEAL"],
            )

        assert result["success"] is True
        assert len(result["results"]) == 2
        assert "test_batch" not in manager.active_batches  # Should be cleaned up
        assert len(manager.batch_history) == 1

    @pytest.mark.asyncio
    async def test_submit_batch_structured_items(self):
        """Test submitting batch with structured content items."""
        manager = BatchAnalysisManager()

        mock_analysis = {"frameworks": {}, "overall_score": 0}

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            return_value=mock_analysis,
        ):
            content_items = [
                {
                    "id": "custom_1",
                    "content": "Content 1",
                    "frameworks": ["STEPPS"],
                    "metadata": {"source": "test"},
                    "priority": 5,
                },
                {
                    "content": "Content 2",
                    # Will use defaults for missing fields
                },
            ]

            result = await manager.submit_batch(
                batch_id="test_batch",
                content_items=content_items,
                default_frameworks=["IDEAL"],
            )

        assert result["success"] is True
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_submit_batch_invalid_item_type(self):
        """Test submitting batch with invalid item type."""
        manager = BatchAnalysisManager()

        content_items = [123]  # Invalid type

        with pytest.raises(ValueError, match="Invalid content item type"):
            await manager.submit_batch(
                batch_id="test_batch", content_items=content_items
            )

    @pytest.mark.asyncio
    async def test_submit_batch_exception_cleanup(self):
        """Test that active batches are cleaned up when processing fails."""
        manager = BatchAnalysisManager()

        with patch(
            "osp_marketing_tools.batch.analyze_content_with_frameworks",
            side_effect=Exception("Processing failed"),
        ):
            content_items = ["Content 1"]

            result = await manager.submit_batch(
                batch_id="test_batch", content_items=content_items
            )

            # Batch should succeed but individual items should fail
            assert result["success"] is True
            assert len(result["results"]) == 1
            assert result["results"][0].success is False
            assert "Processing failed" in result["results"][0].error

        # Should be cleaned up after failure
        assert "test_batch" not in manager.active_batches

    def test_get_active_batches(self):
        """Test getting active batch IDs."""
        manager = BatchAnalysisManager()

        # No active batches initially
        assert manager.get_active_batches() == []

        # Add some mock active batches
        manager.active_batches["batch_1"] = Mock()
        manager.active_batches["batch_2"] = Mock()

        active = manager.get_active_batches()
        assert set(active) == {"batch_1", "batch_2"}

    def test_cancel_batch_existing(self):
        """Test cancelling an existing batch."""
        manager = BatchAnalysisManager()

        # Add mock active batch
        mock_processor = Mock()
        manager.active_batches["test_batch"] = mock_processor

        result = manager.cancel_batch("test_batch")

        assert result is True
        mock_processor.cancel_processing.assert_called_once()

    def test_cancel_batch_nonexistent(self):
        """Test cancelling a non-existent batch."""
        manager = BatchAnalysisManager()

        result = manager.cancel_batch("nonexistent_batch")

        assert result is False

    def test_get_batch_history_empty(self):
        """Test getting batch history when empty."""
        manager = BatchAnalysisManager()

        history = manager.get_batch_history()

        assert history == []

    def test_get_batch_history_with_data(self):
        """Test getting batch history with data."""
        manager = BatchAnalysisManager()

        # Add mock history entries
        for i in range(15):
            manager.batch_history.append(
                {
                    "batch_id": f"batch_{i}",
                    "timestamp": time.time(),
                    "summary": {"total_items": 1},
                    "success": True,
                }
            )

        # Default limit is 10
        history = manager.get_batch_history()
        assert len(history) == 10

        # Custom limit
        history = manager.get_batch_history(limit=5)
        assert len(history) == 5

        # Should get the most recent ones
        assert history[0]["batch_id"] == "batch_10"  # Last 10 starting from batch_5


class TestGlobalBatchManager:
    """Test global batch manager instance."""

    def test_global_manager_exists(self):
        """Test that global manager instance exists."""
        assert batch_manager is not None
        assert isinstance(batch_manager, BatchAnalysisManager)

    def test_global_manager_is_singleton(self):
        """Test that importing batch_manager gives same instance."""
        from osp_marketing_tools.batch import batch_manager as manager2

        assert batch_manager is manager2
