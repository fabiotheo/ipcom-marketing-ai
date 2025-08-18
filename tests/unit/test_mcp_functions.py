"""Unit tests for MCP tool functions."""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from osp_marketing_tools.server import (analyze_content_multi_framework,
                                        benchmark_file_operations,
                                        clear_cache_statistics,
                                        get_cache_statistics,
                                        get_editing_codes,
                                        get_marketing_frameworks_2025,
                                        get_meta_guide,
                                        get_methodology_versions,
                                        get_on_page_seo_guide,
                                        get_seo_frameworks_2025,
                                        get_technical_writing_2025,
                                        get_value_map_positioning_guide,
                                        get_writing_guide, health_check)
from osp_marketing_tools.version import __version__


class TestMCPBasicFunctions:
    """Test basic MCP tool functions."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check function."""
        result = await health_check()

        assert "status" in result
        assert "timestamp" in result
        assert "version" in result
        assert result["status"] in ["healthy", "warning", "critical"]
        assert result["version"] == __version__

    @pytest.mark.asyncio
    async def test_get_methodology_versions(self):
        """Test methodology versions function."""
        result = await get_methodology_versions()

        assert result["success"] is True
        assert "data" in result
        assert "versions" in result["data"]
        assert isinstance(result["data"]["versions"], dict)

    @pytest.mark.asyncio
    async def test_get_cache_statistics(self):
        """Test cache statistics function."""
        result = await get_cache_statistics()

        assert result["success"] is True
        assert "data" in result
        assert "cache_statistics" in result["data"]
        assert isinstance(result["data"]["cache_statistics"], dict)

    @pytest.mark.asyncio
    async def test_clear_cache_statistics(self):
        """Test clearing cache statistics."""
        result = await clear_cache_statistics()

        assert result["success"] is True
        assert "data" in result
        assert "message" in result["data"]


class TestMCPResourceFunctions:
    """Test MCP resource tool functions."""

    @pytest.mark.asyncio
    async def test_get_editing_codes(self):
        """Test getting editing codes."""
        with patch(
            "builtins.open", mock_open(read_data="# Editing Codes\nContent here")
        ):
            with patch("os.path.exists", return_value=True):
                result = await get_editing_codes()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_writing_guide(self):
        """Test getting writing guide."""
        with patch(
            "builtins.open", mock_open(read_data="# Writing Guide\nContent here")
        ):
            with patch("os.path.exists", return_value=True):
                result = await get_writing_guide()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_meta_guide(self):
        """Test getting meta guide."""
        with patch("builtins.open", mock_open(read_data="# Meta Guide\nContent here")):
            with patch("os.path.exists", return_value=True):
                result = await get_meta_guide()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_value_map_positioning_guide(self):
        """Test getting value map positioning guide."""
        with patch("builtins.open", mock_open(read_data="# Value Map\nContent here")):
            with patch("os.path.exists", return_value=True):
                result = await get_value_map_positioning_guide()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_on_page_seo_guide(self):
        """Test getting on-page SEO guide."""
        with patch("builtins.open", mock_open(read_data="# SEO Guide\nContent here")):
            with patch("os.path.exists", return_value=True):
                result = await get_on_page_seo_guide()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_marketing_frameworks_2025(self):
        """Test getting marketing frameworks 2025."""
        with patch(
            "builtins.open", mock_open(read_data="# Marketing Frameworks\nContent here")
        ):
            with patch("os.path.exists", return_value=True):
                result = await get_marketing_frameworks_2025()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_technical_writing_2025(self):
        """Test getting technical writing 2025."""
        with patch(
            "builtins.open", mock_open(read_data="# Technical Writing\nContent here")
        ):
            with patch("os.path.exists", return_value=True):
                result = await get_technical_writing_2025()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]

    @pytest.mark.asyncio
    async def test_get_seo_frameworks_2025(self):
        """Test getting SEO frameworks 2025."""
        with patch(
            "builtins.open", mock_open(read_data="# SEO Frameworks\nContent here")
        ):
            with patch("os.path.exists", return_value=True):
                result = await get_seo_frameworks_2025()

                assert result["success"] is True
                assert "data" in result
                assert "content" in result["data"]


class TestMCPPerformanceFunctions:
    """Test performance-related MCP functions."""

    @pytest.mark.asyncio
    async def test_benchmark_file_operations(self):
        """Test file operations benchmark."""
        with patch("tempfile.NamedTemporaryFile"):
            with patch("builtins.open", mock_open()):
                with patch("os.path.exists", return_value=True):
                    with patch("os.remove"):
                        result = await benchmark_file_operations()

                        assert result["success"] is True
                        assert "data" in result
                        assert "benchmark_results" in result["data"]


class TestMCPAnalysisFunctions:
    """Test analysis-related MCP functions."""

    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return """
        This is a comprehensive guide for software developers.
        We need to identify the target audience and discover their needs.
        Our solution empowers users to implement best practices.
        We help activate engagement and facilitate continuous learning.
        """

    @pytest.mark.asyncio
    async def test_analyze_content_multi_framework(self, sample_content):
        """Test multi-framework content analysis."""
        result = await analyze_content_multi_framework(
            content=sample_content, frameworks=["IDEAL", "STEPPS"]
        )

        assert result["success"] is True
        assert "data" in result
        assert "analysis" in result["data"]
        assert "frameworks" in result["data"]["analysis"]

        # Check that requested frameworks are present
        assert "IDEAL" in result["data"]["analysis"]["frameworks"]
        assert "STEPPS" in result["data"]["analysis"]["frameworks"]

    @pytest.mark.asyncio
    async def test_analyze_content_all_frameworks(self, sample_content):
        """Test analysis with all frameworks."""
        result = await analyze_content_multi_framework(
            content=sample_content, frameworks=["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]
        )

        assert result["success"] is True
        assert len(result["data"]["analysis"]["frameworks"]) == 4

    @pytest.mark.asyncio
    async def test_analyze_content_default_frameworks(self, sample_content):
        """Test analysis with default frameworks (None)."""
        result = await analyze_content_multi_framework(content=sample_content)

        assert result["success"] is True
        assert len(result["data"]["analysis"]["frameworks"]) == 4  # All frameworks

    @pytest.mark.asyncio
    async def test_analyze_content_invalid_input(self):
        """Test analysis with invalid input."""
        # Test empty content
        result = await analyze_content_multi_framework(content="")
        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "content_validation"

    @pytest.mark.asyncio
    async def test_analyze_content_invalid_framework(self, sample_content):
        """Test analysis with invalid framework."""
        result = await analyze_content_multi_framework(
            content=sample_content, frameworks=["INVALID_FRAMEWORK"]
        )

        # Should fail due to strict framework validation
        assert result["success"] is False
        assert "error" in result
        assert "INVALID_FRAMEWORK" in result["error"]


class TestMCPErrorHandling:
    """Test error handling in MCP functions."""

    @pytest.mark.asyncio
    async def test_resource_file_not_found(self):
        """Test handling of missing resource files."""
        from osp_marketing_tools.server import CONTENT_CACHE

        # Clear cache to force file read
        CONTENT_CACHE.clear()

        with patch("osp_marketing_tools.server.os.path.exists", return_value=False):
            result = await get_editing_codes()

            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_file_read_permission_error(self):
        """Test handling of file permission errors."""
        from osp_marketing_tools.server import CONTENT_CACHE

        # Clear cache to force file read
        CONTENT_CACHE.clear()

        with patch("osp_marketing_tools.server.os.path.exists", return_value=True):
            with patch("osp_marketing_tools.server.os.path.getsize", return_value=1000):
                with patch(
                    "builtins.open", side_effect=PermissionError("Access denied")
                ):
                    result = await get_writing_guide()

                    assert result["success"] is False
                    assert "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_analysis_safety(self):
        """Test that concurrent analyses don't interfere."""
        import asyncio

        content = "Test content for concurrent analysis safety testing."

        # Run multiple analyses concurrently
        tasks = [
            analyze_content_multi_framework(content, ["IDEAL"]),
            analyze_content_multi_framework(content, ["STEPPS"]),
            analyze_content_multi_framework(content, ["E-E-A-T"]),
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        for result in results:
            assert result["success"] is True
            assert "data" in result


class TestMCPDataValidation:
    """Test data validation in MCP functions."""

    @pytest.mark.asyncio
    async def test_analysis_result_structure(self):
        """Test that analysis results have proper structure."""
        content = "Expert guide for developers with practical examples and insights."

        result = await analyze_content_multi_framework(content, ["IDEAL"])

        assert result["success"] is True

        # Check top-level structure
        assert "data" in result

        # Check data structure
        data = result["data"]
        assert "analysis" in data
        assert "content_length" in data
        assert "frameworks_analyzed" in data
        assert "metadata" in data

        # Check metadata structure
        metadata = data["metadata"]
        required_metadata = [
            "methodology_version",
            "analysis_timestamp",
            "configuration",
        ]

        for field in required_metadata:
            assert field in metadata

    @pytest.mark.asyncio
    async def test_framework_analysis_structure(self):
        """Test individual framework analysis structure."""
        content = "Comprehensive development guide with expert recommendations."

        result = await analyze_content_multi_framework(content, ["IDEAL"])

        ideal_analysis = result["data"]["analysis"]["frameworks"]["IDEAL"]

        # Check IDEAL components
        expected_components = ["identify", "discover", "empower", "activate", "learn"]

        for component in expected_components:
            assert component in ideal_analysis
            component_data = ideal_analysis[component]
            assert "score" in component_data
            assert "recommendations" in component_data
            assert isinstance(component_data["score"], (int, float))
            assert 0 <= component_data["score"] <= 100
            assert isinstance(component_data["recommendations"], str)
            assert len(component_data["recommendations"]) > 0
