"""Core data structures for Interactive Buyer Persona Generator.

Based on Adele Revella's 5 Rings of Buying Insight methodology from
"Buyer Personas: How to Gain Insight into your Customer's Expectations,
Align your Marketing Strategies, and Win More Business" (2024 Revised Edition).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RingType(Enum):
    """Adele Revella's 5 Rings of Buying Insight."""

    PRIORITY_INITIATIVE = "priority_initiative"
    SUCCESS_FACTORS = "success_factors"
    PERCEIVED_BARRIERS = "perceived_barriers"
    DECISION_CRITERIA = "decision_criteria"
    BUYER_JOURNEY = "buyer_journey"


@dataclass
class PriorityInitiativeInsight:
    """Ring 1: What made the buyer decide they need to solve this problem NOW?"""

    trigger_events: List[str]  # Events that motivated the search for solution
    pain_points: List[str]  # Specific pain points that led to action
    status_quo_failures: List[str]  # Why previous solutions failed
    budget_allocation_triggers: List[str]  # What freed up budget/time
    urgency_level: str = "medium"  # low, medium, high, critical
    political_capital: str = ""  # Internal political factors


@dataclass
class SuccessFactors:
    """Ring 2: What specific results does the buyer expect to achieve?"""

    tangible_outcomes: Dict[str, str]  # {"revenue": "+20%", "cost": "-15%"}
    intangible_outcomes: List[str]  # ["peace of mind", "team productivity"]
    business_impact: List[str]  # Business-level impacts
    personal_impact: List[str]  # Career/personal impacts
    success_metrics: List[str]  # How they measure success
    timeline_expectations: str = ""  # When they expect results


@dataclass
class PerceivedBarriers:
    """Ring 3: What obstacles does the buyer see to implementing our solution?"""

    risk_concerns: List[str]  # Fears about implementation
    past_negative_experiences: List[str]  # Previous bad experiences
    internal_resistance: Dict[str, str]  # {"stakeholder": "reason for resistance"}
    competitive_concerns: List[str]  # Concerns about competitors
    resource_constraints: List[str]  # Perceived limitations
    implementation_fears: List[str] = field(default_factory=list)


@dataclass
class DecisionCriteria:
    """Ring 4: What specific aspects does the buyer evaluate before deciding?"""

    must_have_features: List[str]  # Mandatory criteria
    nice_to_have_features: List[str]  # Desirable criteria
    evaluation_process: List[str]  # How they evaluate vendors
    vendor_selection_factors: List[str]  # Company aspects evaluated
    deal_breakers: List[str]  # What eliminates a vendor
    decision_timeline: str = ""  # How long they take to decide


@dataclass
class BuyerJourney:
    """Ring 5: How exactly does the buyer navigate the decision process?"""

    research_sources: List[str]  # Where they seek information
    trusted_advisors: List[str]  # Who influences decisions
    decision_making_team: Dict[str, str]  # {"role": "influence_level"}
    evaluation_timeline: str  # Typical process duration
    approval_process: List[str]  # Internal approval steps
    content_preferences: Dict[str, List[str]] = field(
        default_factory=dict
    )  # {"stage": ["content_types"]}


@dataclass
class Demographics:
    """Basic demographic information to complement the 5 Rings."""

    age_range: str = ""
    job_title: str = ""
    company_size: str = ""
    industry: str = ""
    location: str = ""
    experience_level: str = ""
    education: str = ""


@dataclass
class DigitalBehavior:
    """Digital and communication preferences."""

    preferred_channels: List[str] = field(default_factory=list)
    communication_style: str = ""  # formal, informal, technical
    device_preferences: List[str] = field(default_factory=list)
    content_consumption_habits: List[str] = field(default_factory=list)
    social_media_usage: Dict[str, str] = field(default_factory=dict)


@dataclass
class BuyerPersonaData:
    """Complete buyer persona based on Adele Revella's 5 Rings methodology."""

    # Core persona identification
    name: str
    persona_id: str = ""

    # Adele Revella's 5 Rings
    priority_initiative: Optional[PriorityInitiativeInsight] = None
    success_factors: Optional[SuccessFactors] = None
    perceived_barriers: Optional[PerceivedBarriers] = None
    decision_criteria: Optional[DecisionCriteria] = None
    buyers_journey: Optional[BuyerJourney] = None

    # Complementary data
    demographics: Demographics = field(default_factory=Demographics)
    digital_behavior: DigitalBehavior = field(default_factory=DigitalBehavior)

    # Metadata and quality tracking
    research_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    ring_confidence_scores: Dict[RingType, float] = field(default_factory=dict)
    source: str = "interview"  # interview, research, hybrid
    validation_flags: Dict[str, bool] = field(default_factory=dict)

    def get_ring_data(self, ring_type: RingType) -> Optional[Any]:
        """Get data for a specific ring."""
        ring_mapping = {
            RingType.PRIORITY_INITIATIVE: self.priority_initiative,
            RingType.SUCCESS_FACTORS: self.success_factors,
            RingType.PERCEIVED_BARRIERS: self.perceived_barriers,
            RingType.DECISION_CRITERIA: self.decision_criteria,
            RingType.BUYER_JOURNEY: self.buyers_journey,
        }
        return ring_mapping.get(ring_type)

    def set_ring_data(self, ring_type: RingType, data: Any) -> None:
        """Set data for a specific ring."""
        if ring_type == RingType.PRIORITY_INITIATIVE:
            self.priority_initiative = data
        elif ring_type == RingType.SUCCESS_FACTORS:
            self.success_factors = data
        elif ring_type == RingType.PERCEIVED_BARRIERS:
            self.perceived_barriers = data
        elif ring_type == RingType.DECISION_CRITERIA:
            self.decision_criteria = data
        elif ring_type == RingType.BUYER_JOURNEY:
            self.buyers_journey = data


@dataclass
class InterviewSession:
    """Tracks an interview session with responses."""

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    responses: Dict[str, str] = field(default_factory=dict)
    current_ring: RingType = RingType.PRIORITY_INITIATIVE
    is_completed: bool = False

    def add_response(self, question_id: str, response: str) -> None:
        """Add a response to the session."""
        self.responses[question_id] = response

    def complete_session(self) -> None:
        """Mark the session as completed."""
        self.is_completed = True
        self.completed_at = datetime.now()


@dataclass
class MarketResearchResult:
    """Result from market research for a specific query."""

    query: str
    results: List[str]
    source: str  # "ddgs", "fallback", "manual"
    success: bool = True
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RingQualityMetrics:
    """Quality metrics for each ring's data."""

    completeness_score: float  # 0-100% of questions answered adequately
    depth_score: float  # 0-100% quality/depth of responses
    consistency_score: float  # 0-100% consistency with other rings
    research_validation_score: float  # 0-100% confirmed by research

    @property
    def overall_score(self) -> float:
        """Calculate overall quality score."""
        return (
            self.completeness_score * 0.3
            + self.depth_score * 0.3
            + self.consistency_score * 0.2
            + self.research_validation_score * 0.2
        )


@dataclass
class ValidationResult:
    """Result of cross-ring validation."""

    passed: bool
    score: float
    issues: List[str]
    suggestions: List[str]
    validation_type: str = ""


@dataclass
class QualityReport:
    """Comprehensive quality report for a persona."""

    overall_confidence: float
    ring_confidence: Dict[str, float]
    validation_results: Dict[str, ValidationResult]
    enhanced_persona: BuyerPersonaData
    improvement_suggestions: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
