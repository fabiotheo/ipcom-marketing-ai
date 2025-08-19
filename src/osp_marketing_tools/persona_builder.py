"""Persona Builder - Core orchestration for Interactive Buyer Persona Generator.

Combines interview data, market research, and quality assurance to generate
complete buyer personas based on Adele Revella's 5 Rings methodology.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .fallback_data_provider import FallbackDataProvider
from .interview_engine import InterviewEngine
from .market_research_engine import MarketResearchEngine
from .persona_data_structures import (
    BuyerJourney,
    BuyerPersonaData,
    DecisionCriteria,
    DigitalBehavior,
    PerceivedBarriers,
    PriorityInitiativeInsight,
    RingType,
    SuccessFactors,
)
from .quality_assurance import PersonaQualityOrchestrator

logger = logging.getLogger(__name__)


class PersonaBuilder:
    """Core orchestrator for the persona generation process."""

    def __init__(self, language: str = "en"):
        """Initialize with specified language support."""
        self.language = language
        self.interview_engine = InterviewEngine(language=language)
        self.research_engine = MarketResearchEngine()
        self.quality_orchestrator = PersonaQualityOrchestrator()
        self.fallback_provider = FallbackDataProvider()

    async def build_persona_from_interview(
        self, session_id: str, persona_name: str = ""
    ) -> Dict[str, Any]:
        """Build complete persona from interview session."""

        logger.info(f"Starting persona building for session {session_id}")

        # Get interview data
        session = self.interview_engine.get_session_data(session_id)
        if not session or not session.is_completed:
            raise ValueError("Interview session not found or not completed")

        # Extract context for market research
        persona_context = self._extract_persona_context(session)

        # Conduct market research
        logger.info("Conducting market research...")
        research_results = await self.research_engine.conduct_batch_research(
            persona_context
        )

        # Build initial persona from interview data
        logger.info("Building persona from interview data...")
        persona_data = self._build_persona_from_responses(session, persona_name)

        # Enhance with research data
        logger.info("Enhancing persona with research insights...")
        enhanced_persona = self._enhance_persona_with_research(
            persona_data, research_results
        )

        # Run quality assurance
        logger.info("Running quality assurance...")
        quality_report = await self.quality_orchestrator.ensure_persona_quality(
            enhanced_persona, self._convert_research_to_dict(research_results)
        )

        # Generate final persona output
        logger.info("Generating final persona output...")
        final_output = self._generate_persona_output(quality_report)

        logger.info(
            f"Persona building completed with {quality_report.overall_confidence:.1f}% confidence"
        )

        return final_output

    def _extract_persona_context(self, session) -> Dict[str, str]:
        """Extract context information for market research."""
        context = {}

        # Extract from responses
        responses = session.responses

        # Get basic demographics
        demographics = self.interview_engine.extract_demographics_from_responses(
            session
        )
        context["industry"] = demographics.industry or "technology"
        context["company_size"] = demographics.company_size or "medium"
        context["job_title"] = demographics.job_title or "manager"

        # Extract product context
        context["product"] = responses.get("product_context", "business solution")

        # Extract key themes from priority initiative
        priority_responses = [
            responses.get("priority_trigger", ""),
            responses.get("priority_pressure", ""),
            responses.get("priority_status_quo", ""),
        ]
        priority_text = " ".join(priority_responses).lower()

        # Simple keyword extraction for research targeting
        if "security" in priority_text or "compliance" in priority_text:
            context["focus_area"] = "security"
        elif "cost" in priority_text or "budget" in priority_text:
            context["focus_area"] = "cost_optimization"
        elif "growth" in priority_text or "scale" in priority_text:
            context["focus_area"] = "scalability"
        else:
            context["focus_area"] = "efficiency"

        return context

    def _build_persona_from_responses(
        self, session, persona_name: str
    ) -> BuyerPersonaData:
        """Build persona data structure from interview responses."""
        responses = session.responses

        # Create base persona
        persona = BuyerPersonaData(
            name=persona_name or f"Persona_{session.session_id[:8]}",
            persona_id=session.session_id,
            source="interview",
            created_at=datetime.now(),
        )

        # Extract demographics
        persona.demographics = (
            self.interview_engine.extract_demographics_from_responses(session)
        )

        # Build Ring 1: Priority Initiative
        persona.priority_initiative = PriorityInitiativeInsight(
            trigger_events=self._extract_list_from_response(
                responses.get("priority_trigger", "")
            ),
            pain_points=self._extract_list_from_response(
                responses.get("priority_pressure", "")
            ),
            status_quo_failures=self._extract_list_from_response(
                responses.get("priority_status_quo", "")
            ),
            budget_allocation_triggers=self._extract_budget_triggers(responses),
            urgency_level=self._assess_urgency_level(responses),
        )

        # Build Ring 2: Success Factors
        persona.success_factors = SuccessFactors(
            tangible_outcomes=self._extract_tangible_outcomes(
                responses.get("success_business", "")
            ),
            intangible_outcomes=self._extract_list_from_response(
                responses.get("success_personal", "")
            ),
            business_impact=self._extract_list_from_response(
                responses.get("success_business", "")
            ),
            personal_impact=self._extract_list_from_response(
                responses.get("success_personal", "")
            ),
            success_metrics=self._extract_success_metrics(
                responses.get("success_timeline", "")
            ),
            timeline_expectations=responses.get("success_timeline", ""),
        )

        # Build Ring 3: Perceived Barriers
        persona.perceived_barriers = PerceivedBarriers(
            risk_concerns=self._extract_list_from_response(
                responses.get("barriers_risks", "")
            ),
            past_negative_experiences=self._extract_past_experiences(responses),
            internal_resistance=self._extract_internal_resistance(
                responses.get("barriers_internal", "")
            ),
            competitive_concerns=self._extract_competitive_concerns(responses),
            resource_constraints=self._extract_resource_constraints(responses),
            implementation_fears=self._extract_implementation_fears(responses),
        )

        # Build Ring 4: Decision Criteria
        persona.decision_criteria = DecisionCriteria(
            must_have_features=self._extract_list_from_response(
                responses.get("criteria_must_have", "")
            ),
            nice_to_have_features=self._extract_nice_to_have(responses),
            evaluation_process=self._extract_list_from_response(
                responses.get("criteria_evaluation", "")
            ),
            vendor_selection_factors=self._extract_list_from_response(
                responses.get("criteria_vendor", "")
            ),
            deal_breakers=self._extract_deal_breakers(responses),
            decision_timeline=self._extract_decision_timeline(responses),
        )

        # Build Ring 5: Buyer's Journey
        persona.buyers_journey = BuyerJourney(
            research_sources=self._extract_list_from_response(
                responses.get("journey_research", "")
            ),
            trusted_advisors=self._extract_trusted_advisors(responses),
            decision_making_team=self._extract_decision_team(
                responses.get("journey_team", "")
            ),
            evaluation_timeline=responses.get("journey_process", ""),
            approval_process=self._extract_approval_process(responses),
            content_preferences=self._extract_content_preferences(responses),
        )

        # Extract digital behavior
        persona.digital_behavior = self._extract_digital_behavior(responses)

        return persona

    def _enhance_persona_with_research(
        self, persona_data: BuyerPersonaData, research_results
    ) -> BuyerPersonaData:
        """Enhance persona with market research insights."""

        # Store research data for quality assessment
        persona_data.research_data = self._convert_research_to_dict(research_results)

        # Simple enhancement: add industry-specific insights
        industry = persona_data.demographics.industry
        if industry and self.fallback_provider.is_industry_supported(industry):

            # Enhance priority initiative with industry triggers
            if persona_data.priority_initiative:
                industry_data = self.fallback_provider.get_ring_fallback(
                    RingType.PRIORITY_INITIATIVE, industry
                )
                if "trigger_events" in industry_data:
                    # Add industry-specific triggers not already mentioned
                    existing_triggers = [
                        t.lower()
                        for t in persona_data.priority_initiative.trigger_events
                    ]
                    for trigger in industry_data["trigger_events"]:
                        if not any(
                            existing in trigger.lower()
                            for existing in existing_triggers
                        ):
                            persona_data.priority_initiative.trigger_events.append(
                                trigger
                            )

            # Similar enhancements for other rings...
            # This is a simplified implementation - production version would be more sophisticated

        return persona_data

    def _generate_persona_output(self, quality_report) -> Dict[str, Any]:
        """Generate final persona output with quality metrics."""
        persona = quality_report.enhanced_persona

        output = {
            "persona": {
                "name": persona.name,
                "id": persona.persona_id,
                "created_at": persona.created_at.isoformat(),
                # Demographics
                "demographics": {
                    "job_title": persona.demographics.job_title,
                    "industry": persona.demographics.industry,
                    "company_size": persona.demographics.company_size,
                    "experience_level": persona.demographics.experience_level,
                },
                # The 5 Rings
                "priority_initiative": self._format_priority_initiative(
                    persona.priority_initiative
                ),
                "success_factors": self._format_success_factors(
                    persona.success_factors
                ),
                "perceived_barriers": self._format_perceived_barriers(
                    persona.perceived_barriers
                ),
                "decision_criteria": self._format_decision_criteria(
                    persona.decision_criteria
                ),
                "buyers_journey": self._format_buyers_journey(persona.buyers_journey),
                # Digital behavior
                "digital_behavior": {
                    "preferred_channels": persona.digital_behavior.preferred_channels,
                    "communication_style": persona.digital_behavior.communication_style,
                    "content_consumption_habits": persona.digital_behavior.content_consumption_habits,
                },
            },
            # Quality metrics
            "quality_metrics": {
                "overall_confidence": quality_report.overall_confidence,
                "ring_confidence": quality_report.ring_confidence,
                "validation_results": {
                    name: {
                        "passed": result.passed,
                        "score": result.score,
                        "issues": result.issues,
                    }
                    for name, result in quality_report.validation_results.items()
                },
                "improvement_suggestions": quality_report.improvement_suggestions,
            },
            # Metadata
            "metadata": {
                "methodology": "Adele Revella's 5 Rings of Buying Insight",
                "source": persona.source,
                "research_data_points": len(persona.research_data),
                "generated_at": datetime.now().isoformat(),
            },
        }

        return output

    # Helper methods for data extraction and formatting

    def _extract_list_from_response(self, response: str) -> List[str]:
        """Extract list items from a text response."""
        if not response:
            return []

        # Simple splitting on common delimiters
        items = []
        for delimiter in [",", ";", "\n", " and ", " & "]:
            if delimiter in response:
                items = [item.strip() for item in response.split(delimiter)]
                break

        if not items:
            items = [response.strip()]

        return [item for item in items if item]

    def _extract_tangible_outcomes(self, response: str) -> Dict[str, str]:
        """Extract tangible outcomes with potential metrics."""
        outcomes = {}

        if not response:
            return outcomes

        # Look for percentage patterns
        import re

        percentages = re.findall(r"(\d+)%", response)
        if percentages:
            outcomes["percentage_improvement"] = f"{percentages[0]}%"

        # Look for dollar amounts
        dollars = re.findall(r"\$([0-9,]+)", response)
        if dollars:
            outcomes["cost_impact"] = f"${dollars[0]}"

        # Look for time savings
        time_patterns = re.findall(r"(\d+)\s+(hours?|minutes?|days?)", response.lower())
        if time_patterns:
            outcomes["time_savings"] = f"{time_patterns[0][0]} {time_patterns[0][1]}"

        # If no specific metrics, use the response as a general outcome
        if not outcomes:
            outcomes["general_outcome"] = response

        return outcomes

    def _assess_urgency_level(self, responses: Dict[str, str]) -> str:
        """Assess urgency level from responses."""
        priority_text = " ".join(
            [
                responses.get("priority_trigger", ""),
                responses.get("priority_pressure", ""),
            ]
        ).lower()

        high_urgency_indicators = [
            "crisis",
            "urgent",
            "immediately",
            "asap",
            "deadline",
            "critical",
        ]
        medium_urgency_indicators = ["soon", "quickly", "priority", "important"]

        if any(indicator in priority_text for indicator in high_urgency_indicators):
            return "high"
        elif any(indicator in priority_text for indicator in medium_urgency_indicators):
            return "medium"
        else:
            return "low"

    def _extract_budget_triggers(self, responses: Dict[str, str]) -> List[str]:
        """Extract what freed up budget/resources."""
        triggers = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["budget", "funding", "approved", "allocated"]
            ):
                triggers.append(response)

        return triggers

    def _extract_success_metrics(self, response: str) -> List[str]:
        """Extract success metrics from response."""
        if not response:
            return []

        metrics = []
        metric_indicators = ["measure", "metric", "kpi", "track", "monitor"]

        sentences = response.split(".")
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in metric_indicators):
                metrics.append(sentence.strip())

        return metrics if metrics else [response]

    def _extract_past_experiences(self, responses: Dict[str, str]) -> List[str]:
        """Extract past negative experiences."""
        experiences = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["previous", "before", "last time", "past", "failed"]
            ):
                experiences.append(response)

        return experiences

    def _extract_internal_resistance(self, response: str) -> Dict[str, str]:
        """Extract internal resistance mapping."""
        if not response:
            return {}

        resistance = {}

        # Simple pattern matching for roles and concerns
        if "team" in response.lower():
            resistance["team"] = response
        if "management" in response.lower() or "manager" in response.lower():
            resistance["management"] = response
        if "it" in response.lower() or "technical" in response.lower():
            resistance["technical_team"] = response

        if not resistance:
            resistance["general"] = response

        return resistance

    def _extract_competitive_concerns(self, responses: Dict[str, str]) -> List[str]:
        """Extract competitive concerns."""
        concerns = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["competitor", "competition", "rival", "alternative"]
            ):
                concerns.append(response)

        return concerns

    def _extract_resource_constraints(self, responses: Dict[str, str]) -> List[str]:
        """Extract resource constraints."""
        constraints = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["budget", "time", "resource", "capacity", "bandwidth"]
            ):
                constraints.append(response)

        return constraints

    def _extract_implementation_fears(self, responses: Dict[str, str]) -> List[str]:
        """Extract implementation-specific fears."""
        fears = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["implement", "deploy", "rollout", "migration", "setup"]
            ):
                fears.append(response)

        return fears

    def _extract_nice_to_have(self, responses: Dict[str, str]) -> List[str]:
        """Extract nice-to-have features."""
        nice_to_have = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["nice", "would be good", "bonus", "plus", "additionally"]
            ):
                nice_to_have.append(response)

        return nice_to_have

    def _extract_deal_breakers(self, responses: Dict[str, str]) -> List[str]:
        """Extract deal breakers."""
        deal_breakers = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["never", "can't", "won't", "deal breaker", "must not"]
            ):
                deal_breakers.append(response)

        return deal_breakers

    def _extract_decision_timeline(self, responses: Dict[str, str]) -> str:
        """Extract decision timeline."""
        timeline_response = responses.get("journey_process", "")

        # Look for time indicators
        import re

        time_patterns = re.findall(
            r"(\d+)\s+(weeks?|months?|days?)", timeline_response.lower()
        )
        if time_patterns:
            return f"{time_patterns[0][0]} {time_patterns[0][1]}"

        return timeline_response

    def _extract_trusted_advisors(self, responses: Dict[str, str]) -> List[str]:
        """Extract trusted advisors."""
        advisors = []

        for response in responses.values():
            if any(
                term in response.lower()
                for term in ["advisor", "consultant", "expert", "trust", "recommend"]
            ):
                advisors.append(response)

        return advisors

    def _extract_decision_team(self, response: str) -> Dict[str, str]:
        """Extract decision team mapping."""
        if not response:
            return {}

        team = {}

        # Simple role identification
        roles = [
            "ceo",
            "cto",
            "manager",
            "director",
            "team lead",
            "developer",
            "analyst",
        ]

        for role in roles:
            if role in response.lower():
                team[role] = f"Involved in {role} capacity"

        if not team:
            team["stakeholder"] = response

        return team

    def _extract_approval_process(self, responses: Dict[str, str]) -> List[str]:
        """Extract approval process steps."""
        steps = []

        process_response = responses.get("journey_process", "")
        if process_response:
            # Look for step indicators
            step_indicators = ["first", "then", "next", "finally", "step", "stage"]
            sentences = process_response.split(".")

            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in step_indicators):
                    steps.append(sentence.strip())

        return steps if steps else [process_response] if process_response else []

    def _extract_content_preferences(
        self, responses: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Extract content preferences by stage."""
        preferences = {}

        research_response = responses.get("journey_research", "")
        if research_response:
            # Simple categorization
            if any(
                term in research_response.lower()
                for term in ["blog", "article", "content"]
            ):
                preferences["awareness"] = ["blogs", "articles"]
            if any(
                term in research_response.lower()
                for term in ["demo", "trial", "comparison"]
            ):
                preferences["consideration"] = ["demos", "trials", "comparisons"]
            if any(
                term in research_response.lower()
                for term in ["case study", "reference", "testimonial"]
            ):
                preferences["decision"] = ["case studies", "references"]

        return preferences

    def _extract_digital_behavior(self, responses: Dict[str, str]) -> DigitalBehavior:
        """Extract digital behavior from responses."""
        digital_behavior = DigitalBehavior()

        # Extract from research sources
        research_response = responses.get("journey_research", "").lower()

        if "linkedin" in research_response:
            digital_behavior.preferred_channels.append("LinkedIn")
        if "google" in research_response:
            digital_behavior.preferred_channels.append("Google Search")
        if "youtube" in research_response:
            digital_behavior.preferred_channels.append("YouTube")
        if "email" in research_response:
            digital_behavior.preferred_channels.append("Email")

        # Assess communication style from overall responses
        all_responses = " ".join(responses.values()).lower()
        if any(term in all_responses for term in ["technical", "detailed", "specific"]):
            digital_behavior.communication_style = "technical"
        elif any(term in all_responses for term in ["simple", "quick", "brief"]):
            digital_behavior.communication_style = "concise"
        else:
            digital_behavior.communication_style = "balanced"

        return digital_behavior

    def _convert_research_to_dict(self, research_results) -> Dict[str, Any]:
        """Convert research results to dictionary for quality assessment."""
        return {result.query: result.results for result in research_results.values()}

    # Formatting methods for output

    def _format_priority_initiative(
        self, priority: Optional[PriorityInitiativeInsight]
    ) -> Dict[str, Any]:
        """Format priority initiative for output."""
        if not priority:
            return {}

        return {
            "trigger_events": priority.trigger_events,
            "pain_points": priority.pain_points,
            "status_quo_failures": priority.status_quo_failures,
            "urgency_level": priority.urgency_level,
            "summary": f"Driven by {priority.urgency_level} urgency due to {', '.join(priority.trigger_events[:2])}",
        }

    def _format_success_factors(
        self, success: Optional[SuccessFactors]
    ) -> Dict[str, Any]:
        """Format success factors for output."""
        if not success:
            return {}

        return {
            "tangible_outcomes": success.tangible_outcomes,
            "intangible_outcomes": success.intangible_outcomes,
            "timeline_expectations": success.timeline_expectations,
            "summary": f"Expects {len(success.tangible_outcomes)} tangible and {len(success.intangible_outcomes)} intangible outcomes",
        }

    def _format_perceived_barriers(
        self, barriers: Optional[PerceivedBarriers]
    ) -> Dict[str, Any]:
        """Format perceived barriers for output."""
        if not barriers:
            return {}

        return {
            "risk_concerns": barriers.risk_concerns,
            "past_negative_experiences": barriers.past_negative_experiences,
            "internal_resistance": barriers.internal_resistance,
            "summary": f"Main concerns: {', '.join(barriers.risk_concerns[:2])}",
        }

    def _format_decision_criteria(
        self, criteria: Optional[DecisionCriteria]
    ) -> Dict[str, Any]:
        """Format decision criteria for output."""
        if not criteria:
            return {}

        return {
            "must_have_features": criteria.must_have_features,
            "evaluation_process": criteria.evaluation_process,
            "vendor_selection_factors": criteria.vendor_selection_factors,
            "deal_breakers": criteria.deal_breakers,
            "summary": f"{len(criteria.must_have_features)} must-have features, {len(criteria.deal_breakers)} deal breakers",
        }

    def _format_buyers_journey(self, journey: Optional[BuyerJourney]) -> Dict[str, Any]:
        """Format buyer's journey for output."""
        if not journey:
            return {}

        return {
            "research_sources": journey.research_sources,
            "trusted_advisors": journey.trusted_advisors,
            "decision_making_team": journey.decision_making_team,
            "evaluation_timeline": journey.evaluation_timeline,
            "approval_process": journey.approval_process,
            "summary": f"Research via {len(journey.research_sources)} sources, {len(journey.decision_making_team)} team members involved",
        }
