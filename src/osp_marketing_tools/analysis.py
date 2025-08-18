"""Content analysis module for OSP Marketing Tools."""

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union


def calculate_score(indicators: int, max_indicators: int = 10) -> float:
    """Calcula score normalizado entre 0-100."""
    return min(100, round((indicators / max_indicators) * 100, 1))


def analyze_keyword_score(
    content: str, keywords: List[str], max_score_items: int = 10
) -> float:
    """Analisa score baseado na presença de palavras-chave."""
    count = sum(1 for keyword in keywords if keyword.lower() in content.lower())
    return calculate_score(count, max_score_items)


def analyze_pattern_score(
    content: str, patterns: List[str], max_score_items: int = 10
) -> float:
    """Analisa score baseado em padrões regex."""
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, content, re.IGNORECASE))
    return calculate_score(count, max_score_items)


def extract_pattern_matches(
    content: str, patterns: List[str], max_matches: int = 5
) -> List[str]:
    """Extrai matches de padrões regex do conteúdo."""
    matches = []
    for pattern in patterns:
        found_matches = re.findall(pattern, content, re.IGNORECASE)
        matches.extend(
            [
                match.strip() if isinstance(match, str) else match
                for match in found_matches[:max_matches]
            ]
        )
    return matches[:max_matches]


def count_content_metrics(content: str) -> Dict[str, int]:
    """Conta métricas básicas do conteúdo."""
    sentences = len(re.findall(r"[.!?]+", content))
    words = len(content.split())
    paragraphs = len([p for p in content.split("\n\n") if p.strip()])

    return {
        "sentences": sentences,
        "words": words,
        "paragraphs": paragraphs,
        "characters": len(content),
        "avg_words_per_sentence": round(words / max(sentences, 1), 1),
    }


class FrameworkAnalyzer:
    """Base class for framework-specific analyzers."""

    def __init__(self, framework_name: str):
        self.framework_name = framework_name

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using framework-specific logic."""
        raise NotImplementedError("Subclasses must implement analyze method")


class IDEALAnalyzer(FrameworkAnalyzer):
    """Analyzer for IDEAL Framework (Identify, Discover, Empower, Activate, Learn)."""

    def __init__(self):
        super().__init__("IDEAL")

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using IDEAL framework."""
        return {
            "identify": self._analyze_target_identification(content),
            "discover": self._analyze_insight_discovery(content),
            "empower": self._analyze_educational_value(content),
            "activate": self._analyze_cta_effectiveness(content),
            "learn": self._analyze_feedback_opportunities(content),
        }

    def _analyze_target_identification(self, content: str) -> Dict[str, Any]:
        """Analisa identificação de público-alvo no conteúdo."""
        audience_keywords = [
            "users",
            "developers",
            "customers",
            "team",
            "audience",
            "personas",
            "stakeholders",
        ]
        pain_keywords = [
            "problem",
            "challenge",
            "issue",
            "difficulty",
            "struggle",
            "pain point",
        ]

        audience_score = analyze_keyword_score(content, audience_keywords, 4)
        pain_score = analyze_keyword_score(content, pain_keywords, 4)

        # Extract audience signals
        audience_patterns = [
            r"(?:for|aimed at|targeting)\s+(\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*)\s+(?:need|want|require)",
            r"if you(?:\s+are)?\s+(\w+(?:\s+\w+)*)",
        ]
        signals = extract_pattern_matches(content, audience_patterns, 5)

        return {
            "score": round((audience_score + pain_score) / 2, 1),
            "audience_score": audience_score,
            "pain_point_score": pain_score,
            "audience_signals": signals,
            "recommendations": "Clarify target audience and pain points",
        }

    def _analyze_insight_discovery(self, content: str) -> Dict[str, Any]:
        """Analisa descoberta de insights únicos."""
        insight_keywords = [
            "insight",
            "discovery",
            "trend",
            "pattern",
            "finding",
            "research",
            "data shows",
        ]
        insight_patterns = [
            r"(?:we found|research shows|data indicates|studies reveal)",
            r"(?:surprisingly|interestingly|notably)",
            r"(?:\d+%|\d+ percent) of",
        ]

        keyword_score = analyze_keyword_score(content, insight_keywords, 6)
        pattern_score = analyze_pattern_score(content, insight_patterns, 4)

        return {
            "score": round((keyword_score + pattern_score) / 2, 1),
            "unique_insights": len(insight_patterns),
            "data_references": len(re.findall(r"\d+%|\d+ percent", content)),
            "recommendations": "Include more data-driven insights",
        }

    def _analyze_educational_value(self, content: str) -> Dict[str, Any]:
        """Analisa valor educacional do conteúdo."""
        educational_keywords = [
            "learn",
            "understand",
            "explain",
            "guide",
            "tutorial",
            "example",
            "step",
        ]
        practical_keywords = [
            "how to",
            "step by step",
            "implementation",
            "practice",
            "apply",
        ]

        educational_score = analyze_keyword_score(content, educational_keywords, 7)
        practical_score = analyze_keyword_score(content, practical_keywords, 5)

        return {
            "score": round((educational_score + practical_score) / 2, 1),
            "educational_elements": educational_score,
            "practical_elements": practical_score,
            "recommendations": "Add more practical examples and guides",
        }

    def _analyze_cta_effectiveness(self, content: str) -> Dict[str, Any]:
        """Analisa efetividade de call-to-action."""
        cta_keywords = [
            "try",
            "start",
            "join",
            "download",
            "subscribe",
            "contact",
            "get started",
        ]
        action_patterns = [
            r"(?:click|visit|go to|check out)",
            r"(?:sign up|register|create account)",
            r"(?:download|install|access)",
        ]

        cta_score = analyze_keyword_score(content, cta_keywords, 7)
        action_score = analyze_pattern_score(content, action_patterns, 5)

        return {
            "score": round((cta_score + action_score) / 2, 1),
            "cta_count": cta_score,
            "action_words": action_score,
            "recommendations": "Strengthen call-to-action clarity",
        }

    def _analyze_feedback_opportunities(self, content: str) -> Dict[str, Any]:
        """Analisa oportunidades de feedback."""
        feedback_keywords = [
            "feedback",
            "comment",
            "review",
            "suggestion",
            "improvement",
            "thoughts",
        ]
        engagement_patterns = [
            r"(?:what do you think|your thoughts|let us know)",
            r"(?:share your|tell us|contact us)",
        ]

        feedback_score = analyze_keyword_score(content, feedback_keywords, 6)
        engagement_score = analyze_pattern_score(content, engagement_patterns, 4)

        return {
            "score": round((feedback_score + engagement_score) / 2, 1),
            "feedback_opportunities": feedback_score,
            "engagement_elements": engagement_score,
            "recommendations": "Add feedback loops and iteration points",
        }


class STEPPSAnalyzer(FrameworkAnalyzer):
    """Analyzer for STEPPS Framework (Social Currency, Triggers, Emotion, Public, Practical Value, Stories)."""

    def __init__(self):
        super().__init__("STEPPS")

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using STEPPS framework."""
        return {
            "social_currency": self._analyze_social_currency(content),
            "triggers": self._analyze_triggers(content),
            "emotion": self._analyze_emotion(content),
            "public": self._analyze_public_visibility(content),
            "practical_value": self._analyze_practical_value(content),
            "stories": self._analyze_storytelling(content),
        }

    def _analyze_social_currency(self, content: str) -> Dict[str, Any]:
        """Analisa elementos que geram social currency."""
        status_keywords = [
            "exclusive",
            "premium",
            "insider",
            "expert",
            "advanced",
            "elite",
            "special",
        ]
        achievement_keywords = [
            "accomplish",
            "master",
            "achieve",
            "succeed",
            "win",
            "excel",
        ]

        status_score = analyze_keyword_score(content, status_keywords, 7)
        achievement_score = analyze_keyword_score(content, achievement_keywords, 6)

        return {
            "score": round((status_score + achievement_score) / 2, 1),
            "status_signals": status_score,
            "achievement_elements": achievement_score,
            "recommendations": "Enhance social currency and status appeal",
        }

    def _analyze_triggers(self, content: str) -> Dict[str, Any]:
        """Analisa triggers que ativam lembrança."""
        time_triggers = ["daily", "weekly", "monthly", "regularly", "often", "always"]
        contextual_triggers = ["when", "if", "during", "while", "whenever"]

        time_score = analyze_keyword_score(content, time_triggers, 6)
        contextual_score = analyze_keyword_score(content, contextual_triggers, 5)

        return {
            "score": round((time_score + contextual_score) / 2, 1),
            "time_triggers": time_score,
            "contextual_triggers": contextual_score,
            "recommendations": "Add more contextual and temporal triggers",
        }

    def _analyze_emotion(self, content: str) -> Dict[str, Any]:
        """Analisa conteúdo emocional."""
        positive_emotions = [
            "excited",
            "amazing",
            "fantastic",
            "love",
            "incredible",
            "wonderful",
        ]
        negative_emotions = [
            "frustrated",
            "annoying",
            "terrible",
            "awful",
            "horrible",
            "disappointing",
        ]

        positive_score = analyze_keyword_score(content, positive_emotions, 6)
        negative_score = analyze_keyword_score(content, negative_emotions, 6)

        return {
            "score": round((positive_score + negative_score) / 2, 1),
            "positive_emotions": positive_score,
            "negative_emotions": negative_score,
            "recommendations": "Incorporate more emotional triggers",
        }

    def _analyze_public_visibility(self, content: str) -> Dict[str, Any]:
        """Analisa elementos de visibilidade pública."""
        sharing_keywords = [
            "share",
            "post",
            "social",
            "public",
            "community",
            "showcase",
        ]
        visibility_keywords = ["visible", "display", "show", "demonstrate", "exhibit"]

        sharing_score = analyze_keyword_score(content, sharing_keywords, 6)
        visibility_score = analyze_keyword_score(content, visibility_keywords, 5)

        return {
            "score": round((sharing_score + visibility_score) / 2, 1),
            "sharing_elements": sharing_score,
            "visibility_elements": visibility_score,
            "recommendations": "Increase public visibility aspects",
        }

    def _analyze_practical_value(self, content: str) -> Dict[str, Any]:
        """Analisa valor prático do conteúdo."""
        utility_keywords = [
            "useful",
            "helpful",
            "practical",
            "valuable",
            "benefit",
            "advantage",
        ]
        instruction_keywords = [
            "how",
            "guide",
            "tutorial",
            "step",
            "method",
            "technique",
        ]

        utility_score = analyze_keyword_score(content, utility_keywords, 6)
        instruction_score = analyze_keyword_score(content, instruction_keywords, 6)

        return {
            "score": round((utility_score + instruction_score) / 2, 1),
            "utility_elements": utility_score,
            "instructional_elements": instruction_score,
            "recommendations": "Enhance practical utility and instructions",
        }

    def _analyze_storytelling(self, content: str) -> Dict[str, Any]:
        """Analisa elementos de storytelling."""
        story_keywords = [
            "story",
            "experience",
            "journey",
            "happened",
            "once",
            "imagine",
        ]
        narrative_keywords = [
            "first",
            "then",
            "finally",
            "before",
            "after",
            "meanwhile",
        ]

        story_score = analyze_keyword_score(content, story_keywords, 6)
        narrative_score = analyze_keyword_score(content, narrative_keywords, 6)

        return {
            "score": round((story_score + narrative_score) / 2, 1),
            "story_elements": story_score,
            "narrative_structure": narrative_score,
            "recommendations": "Strengthen storytelling and narrative flow",
        }


class EEATAnalyzer(FrameworkAnalyzer):
    """Analyzer for E-E-A-T Framework (Experience, Expertise, Authority, Trustworthiness)."""

    def __init__(self):
        super().__init__("E-E-A-T")

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using E-E-A-T framework."""
        return {
            "experience": self._analyze_experience(content),
            "expertise": self._analyze_expertise(content),
            "authority": self._analyze_authority(content),
            "trustworthiness": self._analyze_trustworthiness(content),
        }

    def _analyze_experience(self, content: str) -> Dict[str, Any]:
        """Analisa experiência demonstrada."""
        experience_keywords = [
            "experience",
            "worked",
            "practiced",
            "implemented",
            "tested",
            "tried",
        ]
        personal_keywords = [
            "I",
            "we",
            "our team",
            "my experience",
            "personally",
            "firsthand",
        ]

        experience_score = analyze_keyword_score(content, experience_keywords, 6)
        personal_score = analyze_keyword_score(content, personal_keywords, 4)

        return {
            "score": round((experience_score + personal_score) / 2, 1),
            "experience_indicators": experience_score,
            "personal_touch": personal_score,
            "recommendations": "Add more personal experience examples",
        }

    def _analyze_expertise(self, content: str) -> Dict[str, Any]:
        """Analisa expertise técnica."""
        expertise_keywords = [
            "expert",
            "specialist",
            "professional",
            "certified",
            "qualified",
            "skilled",
        ]
        technical_keywords = [
            "API",
            "SDK",
            "JSON",
            "HTTP",
            "SQL",
            "CSS",
            "HTML",
            "JavaScript",
        ]

        expertise_score = analyze_keyword_score(content, expertise_keywords, 6)
        technical_score = analyze_keyword_score(content, technical_keywords, 8)

        return {
            "score": round((expertise_score + technical_score) / 2, 1),
            "expertise_claims": expertise_score,
            "technical_depth": technical_score,
            "recommendations": "Demonstrate more technical expertise",
        }

    def _analyze_authority(self, content: str) -> Dict[str, Any]:
        """Analisa autoridade no assunto."""
        authority_keywords = [
            "research",
            "study",
            "data",
            "statistics",
            "findings",
            "evidence",
        ]
        citation_patterns = [r"\[[\d\w\s,]+\]", r"according to", r"source:", r"ref:"]

        authority_score = analyze_keyword_score(content, authority_keywords, 6)
        citation_score = analyze_pattern_score(content, citation_patterns, 4)

        return {
            "score": round((authority_score + citation_score) / 2, 1),
            "authority_signals": authority_score,
            "citations": citation_score,
            "recommendations": "Include more authoritative sources and citations",
        }

    def _analyze_trustworthiness(self, content: str) -> Dict[str, Any]:
        """Analisa confiabilidade do conteúdo."""
        trust_keywords = [
            "honest",
            "transparent",
            "accurate",
            "verified",
            "reliable",
            "trustworthy",
        ]
        disclaimer_keywords = [
            "disclaimer",
            "note",
            "warning",
            "caution",
            "important",
            "please note",
        ]

        trust_score = analyze_keyword_score(content, trust_keywords, 6)
        disclaimer_score = analyze_keyword_score(content, disclaimer_keywords, 4)

        return {
            "score": round((trust_score + disclaimer_score) / 2, 1),
            "trust_signals": trust_score,
            "disclaimers": disclaimer_score,
            "recommendations": "Enhance transparency and trustworthiness",
        }


class GDocPAnalyzer(FrameworkAnalyzer):
    """Analyzer for GDocP Framework (Good Documentation Practices)."""

    def __init__(self):
        super().__init__("GDocP")

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using GDocP framework."""
        content_metrics = count_content_metrics(content)

        return {
            "attributable": self._analyze_attribution(content),
            "legible": self._analyze_legibility(content, content_metrics),
            "contemporaneous": self._analyze_timeliness(content),
            "original": self._analyze_originality(content),
            "accurate": self._analyze_accuracy(content),
            "complete": self._analyze_completeness(content),
        }

    def _analyze_attribution(self, content: str) -> Dict[str, Any]:
        """Analisa atribuição e autoria."""
        attribution_keywords = [
            "author",
            "by",
            "written by",
            "created by",
            "contributor",
            "reviewer",
        ]
        responsibility_keywords = [
            "responsible",
            "maintainer",
            "owner",
            "contact",
            "team",
        ]

        attribution_score = analyze_keyword_score(content, attribution_keywords, 6)
        responsibility_score = analyze_keyword_score(
            content, responsibility_keywords, 4
        )

        return {
            "score": round((attribution_score + responsibility_score) / 2, 1),
            "attribution_elements": attribution_score,
            "responsibility_indicators": responsibility_score,
            "recommendations": "Add clear authorship and responsibility information",
        }

    def _analyze_legibility(
        self, content: str, metrics: Dict[str, int]
    ) -> Dict[str, Any]:
        """Analisa legibilidade do conteúdo."""
        structure_score = 100 if metrics["paragraphs"] > 0 else 0
        sentence_length_score = 100 if metrics["avg_words_per_sentence"] <= 20 else 50

        readability_keywords = [
            "clear",
            "simple",
            "easy",
            "understand",
            "explain",
            "overview",
        ]
        readability_score = analyze_keyword_score(content, readability_keywords, 6)

        overall_score = round(
            (structure_score + sentence_length_score + readability_score) / 3, 1
        )

        return {
            "score": overall_score,
            "structure_score": structure_score,
            "sentence_clarity": sentence_length_score,
            "readability_indicators": readability_score,
            "content_metrics": metrics,
            "recommendations": "Optimize structure and clarity",
        }

    def _analyze_timeliness(self, content: str) -> Dict[str, Any]:
        """Analisa atualidade do conteúdo."""
        time_keywords = ["updated", "current", "latest", "recent", "new", "now"]
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{1,2}/\d{1,2}/\d{4}",
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
        ]

        timeliness_score = analyze_keyword_score(content, time_keywords, 6)
        date_references = len(extract_pattern_matches(content, date_patterns, 10))

        return {
            "score": timeliness_score,
            "timeliness_indicators": timeliness_score,
            "date_references": date_references,
            "recommendations": "Add timestamps and update indicators",
        }

    def _analyze_originality(self, content: str) -> Dict[str, Any]:
        """Analisa originalidade do conteúdo."""
        original_keywords = [
            "original",
            "unique",
            "new",
            "innovative",
            "custom",
            "proprietary",
        ]
        research_keywords = [
            "research",
            "study",
            "analysis",
            "investigation",
            "findings",
        ]

        original_score = analyze_keyword_score(content, original_keywords, 6)
        research_score = analyze_keyword_score(content, research_keywords, 5)

        return {
            "score": round((original_score + research_score) / 2, 1),
            "originality_indicators": original_score,
            "research_elements": research_score,
            "recommendations": "Enhance original research and insights",
        }

    def _analyze_accuracy(self, content: str) -> Dict[str, Any]:
        """Analisa precisão do conteúdo."""
        accuracy_keywords = [
            "accurate",
            "correct",
            "precise",
            "exact",
            "verified",
            "validated",
        ]
        fact_patterns = [r"\d+%", r"\d+\.\d+", r"according to", r"source:", r"ref:"]

        accuracy_score = analyze_keyword_score(content, accuracy_keywords, 6)
        fact_claims = len(extract_pattern_matches(content, fact_patterns, 10))

        return {
            "score": accuracy_score,
            "accuracy_indicators": accuracy_score,
            "factual_claims": fact_claims,
            "recommendations": "Verify and cite factual claims",
        }

    def _analyze_completeness(self, content: str) -> Dict[str, Any]:
        """Analisa completude do conteúdo."""
        completeness_keywords = [
            "complete",
            "comprehensive",
            "full",
            "entire",
            "all",
            "everything",
        ]
        coverage_keywords = [
            "overview",
            "summary",
            "conclusion",
            "prerequisites",
            "requirements",
        ]

        completeness_score = analyze_keyword_score(content, completeness_keywords, 6)
        coverage_score = analyze_keyword_score(content, coverage_keywords, 5)

        return {
            "score": round((completeness_score + coverage_score) / 2, 1),
            "completeness_indicators": completeness_score,
            "coverage_elements": coverage_score,
            "recommendations": "Ensure comprehensive topic coverage",
        }


# Framework analyzer factory
FRAMEWORK_ANALYZERS = {
    "IDEAL": IDEALAnalyzer(),
    "STEPPS": STEPPSAnalyzer(),
    "E-E-A-T": EEATAnalyzer(),
    "GDocP": GDocPAnalyzer(),
}


def analyze_content_with_frameworks(
    content: str, frameworks: List[str]
) -> Dict[str, Any]:
    """Analyze content using specified frameworks."""
    results = {}

    for framework in frameworks:
        if framework in FRAMEWORK_ANALYZERS:
            try:
                results[framework] = FRAMEWORK_ANALYZERS[framework].analyze(content)
            except Exception as e:
                results[framework] = {
                    "error": f"Analysis failed: {str(e)}",
                    "score": 0,
                    "recommendations": "Unable to analyze with this framework",
                }
        else:
            results[framework] = {
                "error": f"Framework '{framework}' not supported",
                "score": 0,
                "recommendations": f"Available frameworks: {list(FRAMEWORK_ANALYZERS.keys())}",
            }

    return results
