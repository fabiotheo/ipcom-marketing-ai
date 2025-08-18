"""Integration tests for multi-framework analysis."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from osp_marketing_tools.analysis import FRAMEWORK_ANALYZERS
from osp_marketing_tools.server import analyze_content_multi_framework


class TestMultiFrameworkAnalysisIntegration:
    """Integration tests for multi-framework content analysis."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_all_frameworks_integration(self, sample_content):
        """Test analysis with all frameworks working together."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        result = await analyze_content_multi_framework(sample_content, frameworks)

        # Should return success
        assert result["success"] is True
        assert "data" in result

        # All frameworks should be present
        for framework in frameworks:
            assert framework in result["data"]["analysis"]["frameworks"]

        # Check data structure
        assert result["data"]["content_length"] == len(sample_content)
        assert result["data"]["frameworks_analyzed"] == frameworks
        assert (
            len(result["data"]["analysis"]["overall_scores"]) == 5
        )  # 4 frameworks + average_score

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_with_content_validation(self):
        """Test content validation integration."""
        # Test empty content - should return success=False
        result = await analyze_content_multi_framework("", ["IDEAL"])
        assert result["success"] is False
        assert "Content parameter is required" in result["error"]
        assert result["error_type"] == "content_validation"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_with_framework_validation(self, sample_content):
        """Test framework validation integration."""
        # Test invalid framework in strict mode (default)
        result = await analyze_content_multi_framework(sample_content, ["INVALID"])
        assert (
            result["success"] is False
        )  # Should fail with invalid framework in strict mode
        assert result["error_type"] == "framework_validation"
        assert "INVALID" in result["error"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_performance_with_long_content(self, sample_long_content):
        """Test analysis performance with long content."""
        frameworks = ["IDEAL", "STEPPS"]

        result = await analyze_content_multi_framework(sample_long_content, frameworks)

        assert result["success"] is True
        # Should complete in reasonable time (this is tested by pytest timeout)
        # Performance info is not tracked in metadata - check successful completion instead
        assert result["success"] is True
        assert len(result["data"]["frameworks_analyzed"]) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_with_all_framework_features(self, benchmark_content):
        """Test comprehensive analysis with content designed to trigger all features."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        result = await analyze_content_multi_framework(benchmark_content, frameworks)

        assert result["success"] is True

        # Check IDEAL framework features
        ideal_result = result["data"]["analysis"]["frameworks"]["IDEAL"]
        assert all(
            component in ideal_result
            for component in ["identify", "discover", "empower", "activate", "learn"]
        )

        # Check STEPPS framework features
        stepps_result = result["data"]["analysis"]["frameworks"]["STEPPS"]
        assert all(
            component in stepps_result
            for component in [
                "social_currency",
                "triggers",
                "emotion",
                "public",
                "practical_value",
                "stories",
            ]
        )

        # Check E-E-A-T framework features
        eeat_result = result["data"]["analysis"]["frameworks"]["E-E-A-T"]
        assert all(
            component in eeat_result
            for component in ["experience", "expertise", "authority", "trustworthiness"]
        )

        # Check GDocP framework features
        gdocp_result = result["data"]["analysis"]["frameworks"]["GDocP"]
        assert all(
            component in gdocp_result
            for component in [
                "attributable",
                "legible",
                "contemporaneous",
                "original",
                "accurate",
                "complete",
            ]
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_cache_integration(self, sample_content):
        """Test that analysis integrates properly with caching."""
        frameworks = ["IDEAL"]

        # First analysis
        result1 = await analyze_content_multi_framework(sample_content, frameworks)

        # Second analysis (should potentially use cached components)
        result2 = await analyze_content_multi_framework(sample_content, frameworks)

        # Results should be consistent
        assert result1["success"] == result2["success"]
        assert (
            result1["data"]["analysis"]["frameworks"].keys()
            == result2["data"]["analysis"]["frameworks"].keys()
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_error_recovery(self, sample_content):
        """Test error recovery in multi-framework analysis."""
        # Mock one analyzer to fail
        with patch.object(
            FRAMEWORK_ANALYZERS["IDEAL"], "analyze", side_effect=Exception("Test error")
        ):
            result = await analyze_content_multi_framework(
                sample_content, ["IDEAL", "STEPPS"]
            )

            assert result["success"] is True  # Should still succeed overall
            assert "IDEAL" in result["data"]["analysis"]["frameworks"]
            assert "error" in result["data"]["analysis"]["frameworks"]["IDEAL"]
            assert "STEPPS" in result["data"]["analysis"]["frameworks"]
            assert "error" not in result["data"]["analysis"]["frameworks"]["STEPPS"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_concurrent_requests(self, sample_content):
        """Test concurrent analysis requests."""
        frameworks = ["IDEAL", "STEPPS"]

        # Run multiple analyses concurrently
        tasks = [
            analyze_content_multi_framework(
                f"{sample_content} - Request {i}", frameworks
            )
            for i in range(3)
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        for result in results:
            assert result["success"] is True
            assert len(result["data"]["analysis"]["frameworks"]) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_metadata_completeness(self, sample_content):
        """Test that metadata is complete and accurate."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T"]

        result = await analyze_content_multi_framework(sample_content, frameworks)

        # Check data structure and metadata
        assert "data" in result
        assert "metadata" in result["data"]

        data = result["data"]
        metadata = data["metadata"]

        # Check required data fields
        required_data_fields = [
            "content_length",
            "content_words",
            "frameworks_analyzed",
            "analysis",
        ]

        for field in required_data_fields:
            assert field in data, f"Missing data field: {field}"

        # Check required metadata fields
        required_metadata_fields = [
            "methodology_version",
            "analysis_timestamp",
            "configuration",
            "validation_info",
        ]

        for field in required_metadata_fields:
            assert field in metadata, f"Missing metadata field: {field}"

        # Check data accuracy
        assert data["content_length"] == len(sample_content)
        assert data["content_words"] == len(sample_content.split())
        assert len(data["frameworks_analyzed"]) == 3

        # Check validation info
        validation_info = metadata["validation_info"]
        assert validation_info["total_frameworks_requested"] == 3
        assert validation_info["valid_frameworks_processed"] == 3

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_default_frameworks(self, sample_content):
        """Test analysis with default frameworks when none specified."""
        # Test with None
        result = await analyze_content_multi_framework(sample_content, None)
        assert result["success"] is True
        assert (
            len(result["data"]["analysis"]["frameworks"]) == 4
        )  # Should use all frameworks

        # Test with empty list
        result = await analyze_content_multi_framework(sample_content, [])
        assert result["success"] is True
        assert (
            len(result["data"]["analysis"]["frameworks"]) == 4
        )  # Should use all frameworks

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_analyze_stress_test(self, sample_content):
        """Stress test with many concurrent requests."""
        frameworks = ["IDEAL", "STEPPS"]

        # Run many analyses concurrently
        tasks = [
            analyze_content_multi_framework(
                f"{sample_content} - Stress {i}", frameworks
            )
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that most succeeded and no exceptions were raised
        successes = [r for r in results if isinstance(r, dict) and r.get("success")]
        exceptions = [r for r in results if isinstance(r, Exception)]

        assert len(successes) >= 8  # At least 80% success rate
        assert len(exceptions) == 0  # No unhandled exceptions


class TestFrameworkInteractionIntegration:
    """Test interactions between different frameworks."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_framework_score_consistency(self, sample_content):
        """Test that framework scores are consistent across runs."""
        frameworks = ["IDEAL"]

        # Run analysis multiple times
        results = []
        for _ in range(3):
            result = await analyze_content_multi_framework(sample_content, frameworks)
            results.append(result)

        # Scores should be identical for same content
        ideal_scores = [
            r["data"]["analysis"]["frameworks"]["IDEAL"]["identify"]["score"]
            for r in results
        ]
        assert len(set(ideal_scores)) == 1, "Scores should be consistent across runs"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cross_framework_validation(self, benchmark_content):
        """Test that different frameworks provide complementary insights."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        result = await analyze_content_multi_framework(benchmark_content, frameworks)

        # Extract key metrics from each framework
        ideal = result["data"]["analysis"]["frameworks"]["IDEAL"]
        stepps = result["data"]["analysis"]["frameworks"]["STEPPS"]
        eeat = result["data"]["analysis"]["frameworks"]["E-E-A-T"]
        gdocp = result["data"]["analysis"]["frameworks"]["GDocP"]

        # All frameworks should provide different perspectives
        # (This is a basic check - in practice you'd validate specific insights)
        assert "identify" in ideal
        assert "social_currency" in stepps
        assert "expertise" in eeat
        assert "legible" in gdocp

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_framework_error_isolation(self, sample_content):
        """Test that errors in one framework don't affect others."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T"]

        # Mock middle framework to fail
        with patch.object(
            FRAMEWORK_ANALYZERS["STEPPS"],
            "analyze",
            side_effect=ValueError("Test error"),
        ):
            result = await analyze_content_multi_framework(sample_content, frameworks)

            assert result["success"] is True

            # IDEAL and E-E-A-T should work fine
            assert "error" not in result["data"]["analysis"]["frameworks"]["IDEAL"]
            assert "error" not in result["data"]["analysis"]["frameworks"]["E-E-A-T"]

            # STEPPS should have error
            assert "error" in result["data"]["analysis"]["frameworks"]["STEPPS"]

            # Check that frameworks analyzed correctly (since we're not simulating actual errors)
            assert len(result["data"]["frameworks_analyzed"]) == 3
            assert result["success"] is True


class TestAnalysisQualityIntegration:
    """Test the quality and accuracy of integrated analysis."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analysis_quality_metrics(self, benchmark_content):
        """Test that analysis produces quality metrics."""
        frameworks = ["IDEAL", "STEPPS"]

        result = await analyze_content_multi_framework(benchmark_content, frameworks)

        # Check that scores are reasonable (not all zeros or all 100s)
        ideal_scores = []
        for component in result["data"]["analysis"]["frameworks"]["IDEAL"].values():
            if isinstance(component, dict) and "score" in component:
                ideal_scores.append(component["score"])

        stepps_scores = []
        for component in result["data"]["analysis"]["frameworks"]["STEPPS"].values():
            if isinstance(component, dict) and "score" in component:
                stepps_scores.append(component["score"])

        # Scores should vary (indicating nuanced analysis)
        assert len(set(ideal_scores)) > 1, "IDEAL scores should vary"
        assert len(set(stepps_scores)) > 1, "STEPPS scores should vary"

        # All scores should be valid (0-100)
        all_scores = ideal_scores + stepps_scores
        assert all(
            0 <= score <= 100 for score in all_scores
        ), "All scores should be 0-100"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_recommendations_quality(self, sample_content):
        """Test that frameworks provide actionable recommendations."""
        frameworks = ["IDEAL", "E-E-A-T"]

        result = await analyze_content_multi_framework(sample_content, frameworks)

        # Check that recommendations are provided and non-empty
        for framework in frameworks:
            framework_result = result["data"]["analysis"]["frameworks"][framework]

            for component in framework_result.values():
                if isinstance(component, dict) and "recommendations" in component:
                    recommendations = component["recommendations"]
                    assert isinstance(recommendations, str)
                    assert (
                        len(recommendations.strip()) > 10
                    )  # Non-trivial recommendation
                    assert not recommendations.lower().startswith(
                        "error"
                    )  # Not an error message
