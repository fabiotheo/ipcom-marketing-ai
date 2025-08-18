"""Unit tests for analysis module."""

from typing import Any, Dict

import pytest

from osp_marketing_tools.analysis import (FRAMEWORK_ANALYZERS, EEATAnalyzer,
                                          FrameworkAnalyzer, GDocPAnalyzer,
                                          IDEALAnalyzer, STEPPSAnalyzer,
                                          analyze_content_with_frameworks,
                                          analyze_keyword_score,
                                          analyze_pattern_score,
                                          calculate_score,
                                          count_content_metrics,
                                          extract_pattern_matches)


class TestUtilityFunctions:
    """Test utility functions in analysis module."""

    def test_calculate_score_normal_cases(self):
        """Test calculate_score with normal inputs."""
        assert calculate_score(5, 10) == 50.0
        assert calculate_score(10, 10) == 100.0
        assert calculate_score(0, 10) == 0.0
        assert calculate_score(3, 6) == 50.0

    def test_calculate_score_edge_cases(self):
        """Test calculate_score with edge cases."""
        # Test exceeding max indicators (should cap at 100)
        assert calculate_score(15, 10) == 100.0
        assert calculate_score(20, 10) == 100.0

        # Test with zero max_indicators
        with pytest.raises(ZeroDivisionError):
            calculate_score(5, 0)

    def test_analyze_keyword_score(self, sample_content):
        """Test keyword score analysis."""
        keywords = ["development", "guide", "audience", "research"]
        score = analyze_keyword_score(sample_content, keywords, 4)

        # Should find at least some keywords
        assert isinstance(score, (int, float))  # Can be int or float
        assert 0 <= score <= 100

    def test_analyze_keyword_score_case_insensitive(self):
        """Test that keyword analysis is case insensitive."""
        content = "This is a TEST for Development and GUIDE creation."
        keywords = ["test", "development", "guide"]

        score = analyze_keyword_score(content, keywords, 3)
        assert score == 100.0  # All 3 keywords found

    def test_analyze_keyword_score_empty_inputs(self):
        """Test keyword analysis with empty inputs."""
        # Empty content
        assert analyze_keyword_score("", ["test"], 1) == 0.0

        # Empty keywords
        assert analyze_keyword_score("test content", [], 1) == 0.0

        # Both empty
        assert analyze_keyword_score("", [], 1) == 0.0

    def test_analyze_pattern_score(self):
        """Test pattern score analysis."""
        content = "We found 85% of developers. Research shows 90% improvement."
        patterns = [r"\\d+%", r"research shows", r"we found"]

        score = analyze_pattern_score(content, patterns, 3)
        assert isinstance(score, float)
        assert score > 0  # Should find some patterns

    def test_analyze_pattern_score_case_insensitive(self):
        """Test that pattern analysis is case insensitive."""
        content = "RESEARCH SHOWS interesting results. WE FOUND great data."
        patterns = [r"research shows", r"we found"]

        score = analyze_pattern_score(content, patterns, 2)
        assert score == 100.0  # Both patterns should be found

    def test_extract_pattern_matches(self):
        """Test pattern match extraction."""
        content = "Contact us at info@test.com or support@example.org"
        patterns = [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]

        matches = extract_pattern_matches(content, patterns, 5)
        assert len(matches) == 2
        assert "info@test.com" in matches
        assert "support@example.org" in matches

    def test_extract_pattern_matches_limit(self):
        """Test pattern match extraction with limit."""
        content = "Item 1, Item 2, Item 3, Item 4, Item 5, Item 6"
        patterns = [r"Item \d+"]

        matches = extract_pattern_matches(content, patterns, 3)
        assert len(matches) == 3

    def test_count_content_metrics(self, sample_content):
        """Test content metrics counting."""
        metrics = count_content_metrics(sample_content)

        expected_keys = {
            "sentences",
            "words",
            "paragraphs",
            "characters",
            "avg_words_per_sentence",
        }
        assert set(metrics.keys()) == expected_keys

        assert isinstance(metrics["sentences"], int)
        assert isinstance(metrics["words"], int)
        assert isinstance(metrics["paragraphs"], int)
        assert isinstance(metrics["characters"], int)
        assert isinstance(metrics["avg_words_per_sentence"], float)

        assert metrics["sentences"] > 0
        assert metrics["words"] > 0
        assert metrics["characters"] > 0

    def test_count_content_metrics_empty_content(self):
        """Test content metrics with empty content."""
        metrics = count_content_metrics("")

        assert metrics["sentences"] == 0
        assert metrics["words"] == 0
        assert metrics["paragraphs"] == 0
        assert metrics["characters"] == 0
        assert metrics["avg_words_per_sentence"] == 0.0

    def test_count_content_metrics_edge_cases(self):
        """Test content metrics with edge cases."""
        # Single sentence
        metrics = count_content_metrics("This is one sentence.")
        assert metrics["sentences"] == 1
        assert metrics["avg_words_per_sentence"] == 4.0

        # Multiple paragraphs
        content = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        metrics = count_content_metrics(content)
        assert metrics["paragraphs"] == 3


class TestFrameworkAnalyzer:
    """Test base FrameworkAnalyzer class."""

    def test_framework_analyzer_initialization(self):
        """Test FrameworkAnalyzer initialization."""
        analyzer = FrameworkAnalyzer("TEST")
        assert analyzer.framework_name == "TEST"

    def test_framework_analyzer_abstract_method(self):
        """Test that analyze method is abstract."""
        analyzer = FrameworkAnalyzer("TEST")
        with pytest.raises(NotImplementedError):
            analyzer.analyze("test content")


class TestIDEALAnalyzer:
    """Test IDEAL framework analyzer."""

    @pytest.fixture
    def ideal_analyzer(self):
        """IDEAL analyzer fixture."""
        return IDEALAnalyzer()

    def test_ideal_analyzer_initialization(self, ideal_analyzer):
        """Test IDEAL analyzer initialization."""
        assert ideal_analyzer.framework_name == "IDEAL"

    def test_ideal_analyzer_structure(self, ideal_analyzer, sample_content):
        """Test IDEAL analyzer returns correct structure."""
        result = ideal_analyzer.analyze(sample_content)

        expected_keys = {"identify", "discover", "empower", "activate", "learn"}
        assert set(result.keys()) == expected_keys

        for component in result.values():
            assert "score" in component
            assert "recommendations" in component
            assert isinstance(component["score"], (int, float))
            assert isinstance(component["recommendations"], str)

    def test_ideal_target_identification(self, ideal_analyzer):
        """Test IDEAL target identification analysis."""
        content = "This guide is for developers and users who struggle with deployment issues."
        result = ideal_analyzer.analyze(content)

        identify = result["identify"]
        assert identify["score"] > 0  # Should detect audience and pain points
        assert "audience_score" in identify
        assert "pain_point_score" in identify
        assert "audience_signals" in identify

    def test_ideal_insight_discovery(self, ideal_analyzer):
        """Test IDEAL insight discovery analysis."""
        content = "Our research shows that 85% of teams benefit. Studies reveal interesting patterns."
        result = ideal_analyzer.analyze(content)

        discover = result["discover"]
        assert discover["score"] > 0  # Should detect insights and data
        assert "unique_insights" in discover
        assert "data_references" in discover

    def test_ideal_educational_value(self, ideal_analyzer):
        """Test IDEAL educational value analysis."""
        content = (
            "Learn how to implement this step by step guide with practical examples."
        )
        result = ideal_analyzer.analyze(content)

        empower = result["empower"]
        assert empower["score"] > 0  # Should detect educational elements
        assert "educational_elements" in empower
        assert "practical_elements" in empower

    def test_ideal_cta_effectiveness(self, ideal_analyzer):
        """Test IDEAL call-to-action analysis."""
        content = "Try our solution today. Download now and get started immediately."
        result = ideal_analyzer.analyze(content)

        activate = result["activate"]
        assert activate["score"] > 0  # Should detect CTAs
        assert "cta_count" in activate
        assert "action_words" in activate

    def test_ideal_feedback_opportunities(self, ideal_analyzer):
        """Test IDEAL feedback analysis."""
        content = (
            "Share your feedback and let us know your thoughts about this approach."
        )
        result = ideal_analyzer.analyze(content)

        learn = result["learn"]
        assert learn["score"] > 0  # Should detect feedback opportunities
        assert "feedback_opportunities" in learn
        assert "engagement_elements" in learn


class TestSTEPPSAnalyzer:
    """Test STEPPS framework analyzer."""

    @pytest.fixture
    def stepps_analyzer(self):
        """STEPPS analyzer fixture."""
        return STEPPSAnalyzer()

    def test_stepps_analyzer_initialization(self, stepps_analyzer):
        """Test STEPPS analyzer initialization."""
        assert stepps_analyzer.framework_name == "STEPPS"

    def test_stepps_analyzer_structure(self, stepps_analyzer, sample_content):
        """Test STEPPS analyzer returns correct structure."""
        result = stepps_analyzer.analyze(sample_content)

        expected_keys = {
            "social_currency",
            "triggers",
            "emotion",
            "public",
            "practical_value",
            "stories",
        }
        assert set(result.keys()) == expected_keys

        for component in result.values():
            assert "score" in component
            assert "recommendations" in component

    def test_stepps_social_currency(self, stepps_analyzer):
        """Test STEPPS social currency analysis."""
        content = "Become an expert with our exclusive premium insider knowledge."
        result = stepps_analyzer.analyze(content)

        social = result["social_currency"]
        assert social["score"] > 0
        assert "status_signals" in social
        assert "achievement_elements" in social

    def test_stepps_emotion(self, stepps_analyzer):
        """Test STEPPS emotion analysis."""
        content = "This is absolutely amazing and fantastic! It's incredibly exciting."
        result = stepps_analyzer.analyze(content)

        emotion = result["emotion"]
        assert emotion["score"] > 0
        assert "positive_emotions" in emotion
        assert "negative_emotions" in emotion


class TestEEATAnalyzer:
    """Test E-E-A-T framework analyzer."""

    @pytest.fixture
    def eeat_analyzer(self):
        """E-E-A-T analyzer fixture."""
        return EEATAnalyzer()

    def test_eeat_analyzer_initialization(self, eeat_analyzer):
        """Test E-E-A-T analyzer initialization."""
        assert eeat_analyzer.framework_name == "E-E-A-T"

    def test_eeat_analyzer_structure(self, eeat_analyzer, sample_content):
        """Test E-E-A-T analyzer returns correct structure."""
        result = eeat_analyzer.analyze(sample_content)

        expected_keys = {"experience", "expertise", "authority", "trustworthiness"}
        assert set(result.keys()) == expected_keys

    def test_eeat_expertise(self, eeat_analyzer):
        """Test E-E-A-T expertise analysis."""
        content = "As a certified expert specializing in API development and JavaScript frameworks."
        result = eeat_analyzer.analyze(content)

        expertise = result["expertise"]
        assert expertise["score"] > 0
        assert "expertise_claims" in expertise
        assert "technical_depth" in expertise


class TestGDocPAnalyzer:
    """Test GDocP framework analyzer."""

    @pytest.fixture
    def gdocp_analyzer(self):
        """GDocP analyzer fixture."""
        return GDocPAnalyzer()

    def test_gdocp_analyzer_initialization(self, gdocp_analyzer):
        """Test GDocP analyzer initialization."""
        assert gdocp_analyzer.framework_name == "GDocP"

    def test_gdocp_analyzer_structure(self, gdocp_analyzer, sample_content):
        """Test GDocP analyzer returns correct structure."""
        result = gdocp_analyzer.analyze(sample_content)

        expected_keys = {
            "attributable",
            "legible",
            "contemporaneous",
            "original",
            "accurate",
            "complete",
        }
        assert set(result.keys()) == expected_keys

    def test_gdocp_legibility(self, gdocp_analyzer):
        """Test GDocP legibility analysis."""
        content = "This is clear and simple content.\\n\\nEasy to understand with good structure."
        result = gdocp_analyzer.analyze(content)

        legible = result["legible"]
        assert "structure_score" in legible
        assert "sentence_clarity" in legible
        assert "content_metrics" in legible


class TestFrameworkFactory:
    """Test framework analyzer factory."""

    def test_framework_analyzers_exist(self):
        """Test that all expected analyzers exist in factory."""
        expected_frameworks = {"IDEAL", "STEPPS", "E-E-A-T", "GDocP"}
        assert set(FRAMEWORK_ANALYZERS.keys()) == expected_frameworks

    def test_framework_analyzers_types(self):
        """Test that analyzers are correct types."""
        assert isinstance(FRAMEWORK_ANALYZERS["IDEAL"], IDEALAnalyzer)
        assert isinstance(FRAMEWORK_ANALYZERS["STEPPS"], STEPPSAnalyzer)
        assert isinstance(FRAMEWORK_ANALYZERS["E-E-A-T"], EEATAnalyzer)
        assert isinstance(FRAMEWORK_ANALYZERS["GDocP"], GDocPAnalyzer)


class TestAnalyzeContentWithFrameworks:
    """Test the main analysis function."""

    def test_analyze_single_framework(self, sample_content):
        """Test analysis with single framework."""
        result = analyze_content_with_frameworks(sample_content, ["IDEAL"])

        assert "IDEAL" in result
        assert "identify" in result["IDEAL"]

    def test_analyze_multiple_frameworks(self, sample_content):
        """Test analysis with multiple frameworks."""
        frameworks = ["IDEAL", "STEPPS"]
        result = analyze_content_with_frameworks(sample_content, frameworks)

        assert "IDEAL" in result
        assert "STEPPS" in result

    def test_analyze_all_frameworks(self, sample_content):
        """Test analysis with all frameworks."""
        frameworks = ["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]
        result = analyze_content_with_frameworks(sample_content, frameworks)

        for framework in frameworks:
            assert framework in result

    def test_analyze_invalid_framework(self, sample_content):
        """Test analysis with invalid framework."""
        result = analyze_content_with_frameworks(sample_content, ["INVALID"])

        assert "INVALID" in result
        assert "error" in result["INVALID"]
        assert "not supported" in result["INVALID"]["error"]
        assert result["INVALID"]["score"] == 0

    def test_analyze_mixed_valid_invalid_frameworks(self, sample_content):
        """Test analysis with mix of valid and invalid frameworks."""
        frameworks = ["IDEAL", "INVALID", "STEPPS"]
        result = analyze_content_with_frameworks(sample_content, frameworks)

        # Valid frameworks should work
        assert "IDEAL" in result
        assert "identify" in result["IDEAL"]
        assert "STEPPS" in result

        # Invalid framework should have error
        assert "INVALID" in result
        assert "error" in result["INVALID"]

    def test_analyze_empty_content(self):
        """Test analysis with empty content."""
        result = analyze_content_with_frameworks("", ["IDEAL"])

        assert "IDEAL" in result
        # Should still return structure even with empty content
        assert "identify" in result["IDEAL"]

    def test_analyze_empty_frameworks_list(self, sample_content):
        """Test analysis with empty frameworks list."""
        result = analyze_content_with_frameworks(sample_content, [])

        assert result == {}

    def test_analyze_framework_analysis_exception(self, sample_content, monkeypatch):
        """Test handling of analysis exceptions."""

        # Mock analyzer to raise exception
        def mock_analyze(content):
            raise ValueError("Test exception")

        monkeypatch.setattr(FRAMEWORK_ANALYZERS["IDEAL"], "analyze", mock_analyze)

        result = analyze_content_with_frameworks(sample_content, ["IDEAL"])

        assert "IDEAL" in result
        assert "error" in result["IDEAL"]
        assert "Analysis failed" in result["IDEAL"]["error"]
        assert result["IDEAL"]["score"] == 0
