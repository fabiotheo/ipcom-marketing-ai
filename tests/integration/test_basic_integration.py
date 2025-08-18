"""Basic integration tests for OSP Marketing Tools."""

import asyncio

import pytest

from osp_marketing_tools.server import analyze_content_multi_framework


class TestBasicIntegration:
    """Basic integration tests."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_single_framework_integration(self):
        """Test analysis with a single framework works end-to-end."""
        content = "This is a comprehensive software development guide for experienced developers."
        frameworks = ["IDEAL"]

        result = await analyze_content_multi_framework(content, frameworks)

        assert result["success"] is True
        assert "data" in result
        assert "IDEAL" in result["data"]["analysis"]["frameworks"]
        assert result["data"]["content_length"] == len(content)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_multiple_frameworks_integration(self):
        """Test analysis with multiple frameworks."""
        content = "Expert guide with research data showing 90% improvement. Try our solution today and share your experience."
        frameworks = ["IDEAL", "STEPPS"]

        result = await analyze_content_multi_framework(content, frameworks)

        assert result["success"] is True
        assert "IDEAL" in result["data"]["analysis"]["frameworks"]
        assert "STEPPS" in result["data"]["analysis"]["frameworks"]
        assert len(result["data"]["frameworks_analyzed"]) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_all_frameworks_integration(self):
        """Test analysis with all available frameworks."""
        content = """
        Expert guide for developers with extensive research and practical experience.
        Our studies show 95% improvement in deployment practices.
        Share your feedback and try our recommended approach today.
        Created by certified specialists with 10+ years experience.
        Updated regularly with accurate data and comprehensive coverage.
        """
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        result = await analyze_content_multi_framework(content, frameworks)

        assert result["success"] is True
        assert len(result["data"]["frameworks_analyzed"]) == 4

        # Check that all frameworks return valid scores
        for framework in frameworks:
            assert framework in result["data"]["analysis"]["frameworks"]
            framework_result = result["data"]["analysis"]["frameworks"][framework]
            assert isinstance(framework_result, dict)
            # Each framework should have multiple components with scores
            assert len(framework_result) >= 3

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_content_validation_integration(self):
        """Test content validation works end-to-end."""
        # Test empty content - decorator catches exception and returns error dict
        result = await analyze_content_multi_framework("", ["IDEAL"])
        assert result["success"] is False
        assert "Content validation failed" in result["error"]

        # Test too short content
        result = await analyze_content_multi_framework("short", ["IDEAL"])
        assert result["success"] is False
        assert "Content validation failed" in result["error"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_framework_validation_integration(self):
        """Test framework validation works end-to-end."""
        content = (
            "Valid content for analysis with sufficient length for testing purposes."
        )

        # Test invalid framework (with strict validation) - decorator catches exception
        result = await analyze_content_multi_framework(content, ["INVALID_FRAMEWORK"])
        assert result["success"] is False
        assert "Framework validation failed" in result["error"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analysis_consistency(self):
        """Test that analysis results are consistent across multiple runs."""
        content = "Comprehensive guide for software development with practical examples and expert advice."
        frameworks = ["IDEAL"]

        # Run analysis multiple times
        results = []
        for _ in range(3):
            result = await analyze_content_multi_framework(content, frameworks)
            results.append(result)

        # All results should be successful
        for result in results:
            assert result["success"] is True

        # Scores should be consistent (same content = same scores)
        ideal_scores = []
        for result in results:
            framework_result = result["data"]["analysis"]["frameworks"]["IDEAL"]
            identify_score = framework_result["identify"]["score"]
            ideal_scores.append(identify_score)

        # All scores should be identical
        assert len(set(ideal_scores)) == 1, "Scores should be consistent across runs"

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self):
        """Test concurrent analysis requests."""
        content_base = (
            "Expert development guide with research data and practical examples"
        )
        frameworks = ["IDEAL", "STEPPS"]

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            content = f"{content_base} - Version {i}"
            task = analyze_content_multi_framework(content, frameworks)
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # All should succeed
        for result in results:
            assert result["success"] is True
            assert len(result["data"]["frameworks_analyzed"]) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scores_validation(self):
        """Test that all scores are within valid ranges."""
        content = """
        Expert software development guide created by certified professionals.
        Research shows 95% improvement in deployment success rates.
        Learn practical techniques and share your experience with the community.
        Contact our team for personalized guidance and support.
        """
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]

        result = await analyze_content_multi_framework(content, frameworks)

        assert result["success"] is True

        # Validate all scores are in 0-100 range
        for framework_name, framework_result in result["data"]["analysis"][
            "frameworks"
        ].items():
            for component_name, component_data in framework_result.items():
                if isinstance(component_data, dict) and "score" in component_data:
                    score = component_data["score"]
                    assert (
                        0 <= score <= 100
                    ), f"Score {score} out of range for {framework_name}.{component_name}"
                    assert isinstance(
                        score, (int, float)
                    ), f"Score must be numeric for {framework_name}.{component_name}"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_recommendations_quality(self):
        """Test that all frameworks provide meaningful recommendations."""
        content = (
            "Software development guide with practical examples and expert insights."
        )
        frameworks = ["IDEAL", "STEPPS"]

        result = await analyze_content_multi_framework(content, frameworks)

        assert result["success"] is True

        # Check recommendations quality
        for framework_name, framework_result in result["data"]["analysis"][
            "frameworks"
        ].items():
            for component_name, component_data in framework_result.items():
                if (
                    isinstance(component_data, dict)
                    and "recommendations" in component_data
                ):
                    recommendations = component_data["recommendations"]
                    assert isinstance(
                        recommendations, str
                    ), f"Recommendations must be string for {framework_name}.{component_name}"
                    assert (
                        len(recommendations.strip()) > 10
                    ), f"Recommendations too short for {framework_name}.{component_name}"
                    assert not recommendations.lower().startswith(
                        "error"
                    ), f"Recommendations contain error for {framework_name}.{component_name}"
