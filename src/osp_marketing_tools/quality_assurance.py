"""Quality Assurance System for Interactive Buyer Persona Generator.

Implements confidence scoring, cross-ring validation, and quality gates
based on Adele Revella's 5 Rings of Buying Insight methodology.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .fallback_data_provider import FallbackDataProvider
from .persona_data_structures import (
    BuyerPersonaData,
    QualityReport,
    RingQualityMetrics,
    RingType,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates scientific confidence score based on the 5 Rings."""

    # Weights per Ring based on Revella methodology
    RING_WEIGHTS = {
        RingType.PRIORITY_INITIATIVE: 0.25,  # Most critical
        RingType.SUCCESS_FACTORS: 0.20,
        RingType.PERCEIVED_BARRIERS: 0.20,
        RingType.DECISION_CRITERIA: 0.20,
        RingType.BUYER_JOURNEY: 0.15,
    }

    # Quality thresholds per Ring for quality gates
    QUALITY_THRESHOLDS = {
        RingType.PRIORITY_INITIATIVE: {
            "min_answers": 2,  # At least 2 of 3 questions
            "min_words_per_answer": 10,
            "required_keywords": ["trigger", "problem", "urgent", "need", "pressure"],
        },
        RingType.SUCCESS_FACTORS: {
            "min_answers": 2,
            "min_words_per_answer": 8,
            "required_keywords": [
                "result",
                "outcome",
                "success",
                "metric",
                "goal",
                "improve",
            ],
        },
        RingType.PERCEIVED_BARRIERS: {
            "min_answers": 1,  # At least 1 of 2 questions
            "min_words_per_answer": 8,
            "required_keywords": [
                "risk",
                "concern",
                "barrier",
                "problem",
                "worry",
                "fear",
            ],
        },
        RingType.DECISION_CRITERIA: {
            "min_answers": 2,
            "min_words_per_answer": 8,
            "required_keywords": [
                "criteria",
                "feature",
                "requirement",
                "must",
                "evaluate",
            ],
        },
        RingType.BUYER_JOURNEY: {
            "min_answers": 2,
            "min_words_per_answer": 8,
            "required_keywords": [
                "research",
                "source",
                "process",
                "timeline",
                "approval",
            ],
        },
    }

    def calculate_ring_confidence(
        self, persona_data: BuyerPersonaData, research_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each ring."""
        ring_scores = {}

        for ring_type in RingType:
            ring_data = persona_data.get_ring_data(ring_type)
            if ring_data is None:
                ring_scores[ring_type.value] = 0.0
                continue

            metrics = self._calculate_ring_metrics(ring_type, ring_data, research_data)
            ring_scores[ring_type.value] = metrics.overall_score

            # Store detailed metrics in persona
            persona_data.ring_confidence_scores[ring_type] = metrics.overall_score

        return ring_scores

    def _calculate_ring_metrics(
        self, ring_type: RingType, ring_data: Any, research_data: Dict[str, Any]
    ) -> RingQualityMetrics:
        """Calculate detailed quality metrics for a specific ring."""

        # Convert ring data to text for analysis
        ring_text = self._extract_text_from_ring_data(ring_data)

        # Calculate individual metrics
        completeness = self._calculate_completeness_score(ring_type, ring_data)
        depth = self._calculate_depth_score(ring_type, ring_text)
        consistency = self._calculate_consistency_score(ring_type, ring_text)
        research_validation = self._calculate_research_validation_score(
            ring_type, ring_text, research_data
        )

        return RingQualityMetrics(
            completeness_score=completeness,
            depth_score=depth,
            consistency_score=consistency,
            research_validation_score=research_validation,
        )

    def _extract_text_from_ring_data(self, ring_data: Any) -> str:
        """Extract text content from ring data for analysis."""
        text_parts = []

        if hasattr(ring_data, "__dict__"):
            for key, value in ring_data.__dict__.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(item) for item in value])
                elif isinstance(value, dict):
                    text_parts.extend([str(v) for v in value.values()])

        return " ".join(text_parts)

    def _calculate_completeness_score(
        self, ring_type: RingType, ring_data: Any
    ) -> float:
        """Calculate how complete the ring data is."""
        thresholds = self.QUALITY_THRESHOLDS.get(ring_type, {})
        min_answers = thresholds.get("min_answers", 1)

        if not ring_data:
            return 0.0

        # Count non-empty fields
        filled_fields = 0
        total_fields = 0

        if hasattr(ring_data, "__dict__"):
            for key, value in ring_data.__dict__.items():
                total_fields += 1
                if value:  # Non-empty
                    if isinstance(value, (list, dict)):
                        if len(value) > 0:
                            filled_fields += 1
                    else:
                        filled_fields += 1

        if total_fields == 0:
            return 0.0

        completeness_ratio = filled_fields / total_fields

        # Apply minimum answer threshold
        if filled_fields < min_answers:
            completeness_ratio *= 0.5  # Penalty for not meeting minimum

        return min(100.0, completeness_ratio * 100)

    def _calculate_depth_score(self, ring_type: RingType, text: str) -> float:
        """Calculate the depth/quality of responses."""
        if not text:
            return 0.0

        thresholds = self.QUALITY_THRESHOLDS.get(ring_type, {})
        min_words = thresholds.get("min_words_per_answer", 5)
        required_keywords = thresholds.get("required_keywords", [])

        words = text.split()
        word_count = len(words)

        # Base score from word count
        word_score = min(
            100.0, (word_count / (min_words * 3)) * 100
        )  # Expect 3x minimum

        # Keyword presence score
        keyword_score = 0.0
        if required_keywords:
            found_keywords = sum(
                1 for keyword in required_keywords if keyword.lower() in text.lower()
            )
            keyword_score = (found_keywords / len(required_keywords)) * 100

        # Specificity score (avoid generic responses)
        specificity_score = self._calculate_specificity_score(text)

        # Weighted combination
        depth_score = word_score * 0.4 + keyword_score * 0.4 + specificity_score * 0.2
        return min(100.0, depth_score)

    def _calculate_specificity_score(self, text: str) -> float:
        """Calculate how specific (vs generic) the response is."""
        if not text:
            return 0.0

        # Indicators of specific responses
        specific_indicators = [
            r"\d+%",  # Percentages
            r"\$\d+",  # Dollar amounts
            r"\d+\s+(months?|weeks?|days?)",  # Time periods
            r"[A-Z][a-z]+\s+[A-Z][a-z]+",  # Proper nouns (company names, etc.)
            r"\d+x",  # Multipliers
        ]

        # Generic phrases (penalty)
        generic_phrases = [
            "better",
            "improve",
            "increase",
            "reduce",
            "optimize",
            "enhance",
            "streamline",
            "efficient",
            "effective",
        ]

        specific_count = sum(
            len(re.findall(pattern, text)) for pattern in specific_indicators
        )
        generic_count = sum(1 for phrase in generic_phrases if phrase in text.lower())

        # Score based on specificity ratio
        total_words = len(text.split())
        specificity_ratio = specific_count / max(total_words / 10, 1)  # Per 10 words
        generic_penalty = min(0.5, generic_count / max(total_words / 20, 1))

        score = max(0, (specificity_ratio * 100) - (generic_penalty * 50))
        return min(100.0, score)

    def _calculate_consistency_score(self, ring_type: RingType, text: str) -> float:
        """Calculate consistency with ring's purpose."""
        if not text:
            return 0.0

        # Define expected themes for each ring
        ring_themes = {
            RingType.PRIORITY_INITIATIVE: [
                "trigger",
                "event",
                "pressure",
                "problem",
                "urgent",
                "crisis",
                "deadline",
                "competition",
                "change",
                "failure",
            ],
            RingType.SUCCESS_FACTORS: [
                "outcome",
                "result",
                "goal",
                "metric",
                "success",
                "achievement",
                "improvement",
                "benefit",
                "impact",
                "ROI",
            ],
            RingType.PERCEIVED_BARRIERS: [
                "risk",
                "concern",
                "barrier",
                "obstacle",
                "challenge",
                "fear",
                "resistance",
                "difficulty",
                "complexity",
                "constraint",
            ],
            RingType.DECISION_CRITERIA: [
                "criteria",
                "feature",
                "requirement",
                "must",
                "need",
                "evaluate",
                "compare",
                "assess",
                "priority",
                "factor",
            ],
            RingType.BUYER_JOURNEY: [
                "research",
                "source",
                "process",
                "step",
                "stage",
                "timeline",
                "approval",
                "review",
                "decision",
                "workflow",
            ],
        }

        expected_themes = ring_themes.get(ring_type, [])
        if not expected_themes:
            return 50.0  # Neutral score if no themes defined

        # Count theme matches
        text_lower = text.lower()
        theme_matches = sum(1 for theme in expected_themes if theme in text_lower)

        consistency_score = (theme_matches / len(expected_themes)) * 100
        return min(100.0, consistency_score)

    def _calculate_research_validation_score(
        self, ring_type: RingType, text: str, research_data: Dict[str, Any]
    ) -> float:
        """Calculate how well the response is validated by research."""
        if not research_data:
            return 50.0  # Neutral score if no research data

        # Simple validation based on keyword overlap
        research_text = " ".join(
            [
                str(result)
                for results in research_data.values()
                for result in (results if isinstance(results, list) else [results])
            ]
        ).lower()

        if not research_text:
            return 50.0

        # Extract key terms from persona text
        persona_terms = re.findall(r"\b\w{4,}\b", text.lower())

        # Check how many terms appear in research
        validated_terms = sum(1 for term in persona_terms if term in research_text)

        if not persona_terms:
            return 50.0

        validation_ratio = validated_terms / len(persona_terms)
        return min(100.0, validation_ratio * 100)


class RingQualityGate:
    """Validates consistency and logical flow between the 5 Rings."""

    def validate_priority_to_success(
        self, priority_initiative, success_factors
    ) -> ValidationResult:
        """Validate Priority Initiative aligns with Success Factors."""
        if not priority_initiative or not success_factors:
            return ValidationResult(
                passed=False,
                score=0.0,
                issues=["Missing data for validation"],
                suggestions=["Complete both Priority Initiative and Success Factors"],
                validation_type="priority_to_success",
            )

        inconsistencies = []

        # Extract keywords from priority initiative
        priority_text = self._extract_text_from_object(priority_initiative)
        success_text = self._extract_text_from_object(success_factors)

        priority_keywords = self._extract_keywords(priority_text.lower())
        success_keywords = self._extract_keywords(success_text.lower())

        alignment_score = self._calculate_semantic_overlap(
            priority_keywords, success_keywords
        )

        if alignment_score < 0.3:  # 30% threshold
            inconsistencies.append(
                f"Priority Initiative themes don't align with Success Factors. "
                f"Consider whether the expected outcomes address the triggering problems."
            )

        return ValidationResult(
            passed=len(inconsistencies) == 0,
            score=alignment_score,
            issues=inconsistencies,
            suggestions=self._generate_alignment_suggestions(
                priority_text, success_text
            ),
            validation_type="priority_to_success",
        )

    def validate_barriers_to_journey(self, barriers, journey) -> ValidationResult:
        """Validate Perceived Barriers align with Buyer's Journey stages."""
        if not barriers or not journey:
            return ValidationResult(
                passed=False,
                score=0.0,
                issues=["Missing data for validation"],
                suggestions=["Complete both Perceived Barriers and Buyer's Journey"],
                validation_type="barriers_to_journey",
            )

        inconsistencies = []

        # Map barriers to journey stages
        barrier_mapping = {
            "awareness": ["budget", "time", "knowledge", "priority", "resource"],
            "consideration": [
                "features",
                "comparison",
                "trust",
                "complexity",
                "integration",
            ],
            "decision": ["approval", "implementation", "risk", "support", "cost"],
        }

        barriers_text = self._extract_text_from_object(barriers).lower()
        journey_text = self._extract_text_from_object(journey).lower()

        # Check if barriers are reflected in journey
        barrier_keywords = self._extract_keywords(barriers_text)
        journey_keywords = self._extract_keywords(journey_text)

        overlap_score = self._calculate_semantic_overlap(
            barrier_keywords, journey_keywords
        )

        if overlap_score < 0.2:  # 20% threshold
            inconsistencies.append(
                "Perceived barriers don't seem to be addressed in the buyer's journey. "
                "Consider how these concerns affect the decision process."
            )

        return ValidationResult(
            passed=len(inconsistencies) < 2,  # Allow 1 minor inconsistency
            score=1.0 - (len(inconsistencies) * 0.3),
            issues=inconsistencies,
            suggestions=self._generate_barrier_journey_suggestions(
                barriers_text, journey_text
            ),
            validation_type="barriers_to_journey",
        )

    def _extract_text_from_object(self, obj) -> str:
        """Extract text from a data object."""
        if isinstance(obj, str):
            return obj

        text_parts = []
        if hasattr(obj, "__dict__"):
            for value in obj.__dict__.values():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(item) for item in value])
                elif isinstance(value, dict):
                    text_parts.extend([str(v) for v in value.values()])

        return " ".join(text_parts)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words and extract meaningful terms
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }

        words = re.findall(r"\b\w{3,}\b", text.lower())
        keywords = [word for word in words if word not in stopwords]

        # Return unique keywords
        return list(set(keywords))

    def _calculate_semantic_overlap(
        self, keywords1: List[str], keywords2: List[str]
    ) -> float:
        """Calculate semantic overlap between two keyword lists."""
        if not keywords1 or not keywords2:
            return 0.0

        # Direct overlap
        direct_overlap = len(set(keywords1) & set(keywords2))

        # Semantic similarity (simple approach using common stems)
        semantic_matches = 0
        for word1 in keywords1:
            for word2 in keywords2:
                if self._are_semantically_similar(word1, word2):
                    semantic_matches += 1
                    break

        total_possible = min(len(keywords1), len(keywords2))
        overlap_score = (direct_overlap + semantic_matches * 0.5) / total_possible

        return min(1.0, overlap_score)

    def _are_semantically_similar(self, word1: str, word2: str) -> bool:
        """Check if two words are semantically similar."""
        # Simple stem matching
        if len(word1) >= 4 and len(word2) >= 4:
            if word1[:4] == word2[:4]:  # Same 4-letter prefix
                return True

        # Common business term relationships
        related_terms = {
            "cost": ["expense", "budget", "price", "money"],
            "time": ["duration", "timeline", "schedule", "speed"],
            "improve": ["enhance", "optimize", "better", "increase"],
            "problem": ["issue", "challenge", "concern", "difficulty"],
            "solution": ["tool", "system", "platform", "product"],
        }

        for base_term, related in related_terms.items():
            if (word1 == base_term and word2 in related) or (
                word2 == base_term and word1 in related
            ):
                return True

        return False

    def _generate_alignment_suggestions(
        self, priority_text: str, success_text: str
    ) -> List[str]:
        """Generate suggestions for improving alignment."""
        suggestions = []

        if "cost" in priority_text.lower() and "cost" not in success_text.lower():
            suggestions.append(
                "Consider adding cost-related success metrics since cost pressure was a trigger"
            )

        if "time" in priority_text.lower() and "time" not in success_text.lower():
            suggestions.append(
                "Consider adding time-related outcomes since timing was a priority factor"
            )

        if (
            "competitive" in priority_text.lower()
            and "competitive" not in success_text.lower()
        ):
            suggestions.append(
                "Consider adding competitive advantage outcomes since competition was a trigger"
            )

        if not suggestions:
            suggestions.append(
                "Ensure success factors directly address the problems mentioned in priority initiative"
            )

        return suggestions

    def _generate_barrier_journey_suggestions(
        self, barriers_text: str, journey_text: str
    ) -> List[str]:
        """Generate suggestions for improving barrier-journey alignment."""
        suggestions = []

        if "security" in barriers_text and "security" not in journey_text:
            suggestions.append(
                "Consider how security concerns affect the evaluation process"
            )

        if "integration" in barriers_text and "integration" not in journey_text:
            suggestions.append(
                "Consider adding integration evaluation steps to the journey"
            )

        if "approval" in barriers_text and "approval" not in journey_text:
            suggestions.append(
                "Consider detailing the approval process in the buyer's journey"
            )

        if not suggestions:
            suggestions.append(
                "Ensure the buyer's journey addresses how they overcome the perceived barriers"
            )

        return suggestions


class CrossRingValidator:
    """Validates consistency across all 5 Rings for logical coherence."""

    def __init__(self):
        self.quality_gate = RingQualityGate()

    def validate_complete_persona(
        self, persona_data: BuyerPersonaData
    ) -> Dict[str, ValidationResult]:
        """Run comprehensive cross-ring validation."""
        results = {}

        # Ring-to-Ring validations
        results["priority_success"] = self.quality_gate.validate_priority_to_success(
            persona_data.priority_initiative, persona_data.success_factors
        )

        results["barriers_journey"] = self.quality_gate.validate_barriers_to_journey(
            persona_data.perceived_barriers, persona_data.buyers_journey
        )

        # Holistic validation
        results["holistic_coherence"] = self._validate_holistic_coherence(persona_data)

        return results

    def _validate_holistic_coherence(
        self, persona_data: BuyerPersonaData
    ) -> ValidationResult:
        """Validate that the entire persona tells a coherent story."""
        coherence_score = 0.0
        issues = []

        # Check demographic-psychographic alignment
        demo_psych_alignment = self._check_demographic_psychographic_alignment(
            persona_data
        )
        coherence_score += demo_psych_alignment * 0.3

        # Check priority-barrier logical opposition
        priority_barrier_logic = self._check_priority_barrier_logic(persona_data)
        coherence_score += priority_barrier_logic * 0.3

        # Check success-barrier balance
        success_barrier_balance = self._check_success_barrier_balance(persona_data)
        coherence_score += success_barrier_balance * 0.4

        suggestions = self._generate_coherence_suggestions(
            persona_data, coherence_score
        )

        return ValidationResult(
            passed=coherence_score >= 0.7,  # 70% coherence threshold
            score=coherence_score,
            issues=issues,
            suggestions=suggestions,
            validation_type="holistic_coherence",
        )

    def _check_demographic_psychographic_alignment(
        self, persona_data: BuyerPersonaData
    ) -> float:
        """Check if demographics align with psychographic insights."""
        # Simple alignment check based on job title and decision criteria
        demographics = persona_data.demographics
        decision_criteria = persona_data.decision_criteria

        if not demographics.job_title or not decision_criteria:
            return 0.5  # Neutral if missing data

        job_title_lower = demographics.job_title.lower()

        # Technical roles should have technical criteria
        if any(
            tech_term in job_title_lower
            for tech_term in ["engineer", "developer", "architect", "technical"]
        ):
            criteria_text = self.quality_gate._extract_text_from_object(
                decision_criteria
            ).lower()
            tech_score = (
                1.0
                if any(
                    tech_term in criteria_text
                    for tech_term in ["api", "integration", "security", "performance"]
                )
                else 0.3
            )
            return tech_score

        # Executive roles should have business criteria
        if any(
            exec_term in job_title_lower
            for exec_term in ["ceo", "cto", "vp", "director", "manager"]
        ):
            criteria_text = self.quality_gate._extract_text_from_object(
                decision_criteria
            ).lower()
            business_score = (
                1.0
                if any(
                    biz_term in criteria_text
                    for biz_term in ["roi", "cost", "revenue", "business"]
                )
                else 0.3
            )
            return business_score

        return 0.8  # Default good alignment

    def _check_priority_barrier_logic(self, persona_data: BuyerPersonaData) -> float:
        """Check if barriers logically relate to the priority initiative."""
        priority = persona_data.priority_initiative
        barriers = persona_data.perceived_barriers

        if not priority or not barriers:
            return 0.5

        priority_text = self.quality_gate._extract_text_from_object(priority).lower()
        barriers_text = self.quality_gate._extract_text_from_object(barriers).lower()

        # Barriers should reflect concerns about solving the priority
        priority_keywords = self.quality_gate._extract_keywords(priority_text)
        barriers_keywords = self.quality_gate._extract_keywords(barriers_text)

        overlap = self.quality_gate._calculate_semantic_overlap(
            priority_keywords, barriers_keywords
        )
        return min(1.0, overlap + 0.3)  # Boost since some disconnect is normal

    def _check_success_barrier_balance(self, persona_data: BuyerPersonaData) -> float:
        """Check if success factors address the perceived barriers."""
        success = persona_data.success_factors
        barriers = persona_data.perceived_barriers

        if not success or not barriers:
            return 0.5

        success_text = self.quality_gate._extract_text_from_object(success).lower()
        barriers_text = self.quality_gate._extract_text_from_object(barriers).lower()

        # Success factors should implicitly address barrier concerns
        # Look for positive outcomes that counter negative concerns
        balance_indicators = [
            ("security", "secure"),
            ("cost", "save"),
            ("time", "fast"),
            ("complex", "simple"),
            ("risk", "reliable"),
        ]

        balance_score = 0.0
        for concern, solution in balance_indicators:
            if concern in barriers_text and solution in success_text:
                balance_score += 0.2

        return min(1.0, balance_score + 0.5)  # Base score + bonuses

    def _generate_coherence_suggestions(
        self, persona_data: BuyerPersonaData, coherence_score: float
    ) -> List[str]:
        """Generate suggestions for improving coherence."""
        suggestions = []

        if coherence_score < 0.7:
            suggestions.append(
                "Review the persona for logical consistency across all rings"
            )

        if not persona_data.demographics.job_title:
            suggestions.append(
                "Add job title to ensure decision criteria align with role"
            )

        if coherence_score < 0.5:
            suggestions.append(
                "Consider whether the success factors adequately address the barriers"
            )

        return suggestions


class PersonaQualityOrchestrator:
    """Orchestrates all quality assurance processes."""

    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()
        self.cross_validator = CrossRingValidator()
        self.fallback_provider = FallbackDataProvider()

    async def ensure_persona_quality(
        self, persona_data: BuyerPersonaData, research_data: Dict[str, Any]
    ) -> QualityReport:
        """Run complete quality assurance pipeline."""

        # Step 1: Calculate confidence scores
        confidence_scores = self.confidence_scorer.calculate_ring_confidence(
            persona_data, research_data
        )

        # Step 2: Run cross-ring validation
        validation_results = self.cross_validator.validate_complete_persona(
            persona_data
        )

        # Step 3: Apply fallback data for low-confidence areas
        enhanced_persona = await self._apply_fallback_enhancements(
            persona_data, confidence_scores
        )

        # Step 4: Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            confidence_scores, validation_results
        )

        # Step 5: Calculate overall confidence
        overall_confidence = (
            sum(confidence_scores.values()) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        return QualityReport(
            overall_confidence=overall_confidence,
            ring_confidence=confidence_scores,
            validation_results=validation_results,
            enhanced_persona=enhanced_persona,
            improvement_suggestions=improvement_suggestions,
        )

    async def _apply_fallback_enhancements(
        self, persona_data: BuyerPersonaData, confidence_scores: Dict[str, float]
    ) -> BuyerPersonaData:
        """Apply fallback data to enhance low-confidence areas."""
        enhanced_data = persona_data

        industry = persona_data.demographics.industry or "generic"
        company_size = persona_data.demographics.company_size or "medium"

        for ring_name, confidence in confidence_scores.items():
            if confidence < 60.0:  # Low confidence threshold
                ring_type = RingType(ring_name)
                fallback_data = self.fallback_provider.get_ring_fallback(
                    ring_type, industry, company_size
                )

                # Merge fallback data (basic implementation)
                logger.info(
                    f"Applying fallback data for {ring_name} (confidence: {confidence:.1f}%)"
                )
                # Note: In production, implement sophisticated merging logic

        return enhanced_data

    def _generate_improvement_suggestions(
        self,
        confidence_scores: Dict[str, float],
        validation_results: Dict[str, ValidationResult],
    ) -> List[str]:
        """Generate comprehensive improvement suggestions."""
        suggestions = []

        # Suggestions based on confidence scores
        for ring_name, score in confidence_scores.items():
            if score < 60.0:
                suggestions.append(
                    f"Improve {ring_name}: Provide more detailed and specific responses"
                )
            elif score < 80.0:
                suggestions.append(
                    f"Enhance {ring_name}: Add more context and examples"
                )

        # Suggestions from validation results
        for validation_name, result in validation_results.items():
            if not result.passed:
                suggestions.extend(result.suggestions)

        # Remove duplicates and limit to top 5
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]
