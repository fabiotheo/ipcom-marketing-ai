"""Interview Engine for Interactive Buyer Persona Generator.

Implements guided interview based on Adele Revella's 5 Rings of Buying Insight,
with dynamic questioning and context-aware follow-ups.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .persona_data_structures import (
    BuyerJourney,
    DecisionCriteria,
    Demographics,
    DigitalBehavior,
    InterviewSession,
    PerceivedBarriers,
    PriorityInitiativeInsight,
    RingType,
    SuccessFactors,
)

logger = logging.getLogger(__name__)


class InterviewQuestionBank:
    """Structured question bank based on Adele Revella's 5 Rings methodology."""

    # Core questions for each Ring
    RING_QUESTIONS = {
        RingType.PRIORITY_INITIATIVE: [
            {
                "id": "priority_trigger",
                "question": "What specific event or situation made you realize you needed to solve this problem NOW?",
                "context": "Understanding the trigger event is crucial - was it a crisis, opportunity, or deadline?",
                "required": True,
                "follow_up": "Can you describe the business impact of not solving this problem?",
            },
            {
                "id": "priority_pressure",
                "question": "What pressure (internal or external) is driving the urgency to make this decision?",
                "context": "This could be competitive pressure, regulatory requirements, customer demands, etc.",
                "required": True,
                "follow_up": "Who or what is the source of this pressure?",
            },
            {
                "id": "priority_status_quo",
                "question": "What's not working with your current solution or approach?",
                "context": "Understanding current pain points helps identify what triggered the search.",
                "required": False,
                "follow_up": "How long have you been dealing with this problem?",
            },
        ],
        RingType.SUCCESS_FACTORS: [
            {
                "id": "success_business",
                "question": "What specific business results do you expect to achieve with this solution?",
                "context": "Look for measurable outcomes like revenue, cost savings, efficiency gains.",
                "required": True,
                "follow_up": "How would you measure success in 6 months?",
            },
            {
                "id": "success_personal",
                "question": "How will solving this problem impact you personally or professionally?",
                "context": "Personal motivations often drive decision-making more than business reasons.",
                "required": True,
                "follow_up": "What happens to your role if this project succeeds or fails?",
            },
            {
                "id": "success_timeline",
                "question": "When do you need to see results, and what would those early wins look like?",
                "context": "Understanding timeline expectations helps frame the urgency and priorities.",
                "required": False,
                "follow_up": "What would convince stakeholders this was the right decision?",
            },
        ],
        RingType.PERCEIVED_BARRIERS: [
            {
                "id": "barriers_risks",
                "question": "What concerns or risks do you see with implementing a solution like this?",
                "context": "Barriers often come from past bad experiences or known industry challenges.",
                "required": True,
                "follow_up": "Have you or your team had negative experiences with similar solutions before?",
            },
            {
                "id": "barriers_internal",
                "question": "What internal resistance or obstacles do you anticipate?",
                "context": "Internal politics, budget constraints, and change resistance are common barriers.",
                "required": False,
                "follow_up": "Who might be skeptical of this change and why?",
            },
        ],
        RingType.DECISION_CRITERIA: [
            {
                "id": "criteria_must_have",
                "question": "What features or capabilities are absolutely essential for any solution you consider?",
                "context": "These are the non-negotiables that will eliminate vendors from consideration.",
                "required": True,
                "follow_up": "What would be an automatic deal-breaker?",
            },
            {
                "id": "criteria_evaluation",
                "question": "How will you evaluate and compare different options?",
                "context": "Understanding their evaluation process helps frame the competition.",
                "required": True,
                "follow_up": "Who else is involved in this evaluation process?",
            },
            {
                "id": "criteria_vendor",
                "question": "Beyond the product itself, what do you look for in a vendor or partner?",
                "context": "Company factors like size, stability, support quality often influence decisions.",
                "required": False,
                "follow_up": "How important is the vendor's industry experience?",
            },
        ],
        RingType.BUYER_JOURNEY: [
            {
                "id": "journey_research",
                "question": "Where do you typically go to research solutions like this?",
                "context": "Understanding research sources helps with content strategy and channel selection.",
                "required": True,
                "follow_up": "Who do you trust for advice on decisions like this?",
            },
            {
                "id": "journey_process",
                "question": "Walk me through your typical decision-making process for business purchases.",
                "context": "Understanding the formal and informal approval process is crucial.",
                "required": True,
                "follow_up": "How long do decisions like this typically take?",
            },
            {
                "id": "journey_team",
                "question": "Who else is involved in this decision, and what role does each person play?",
                "context": "Mapping the decision-making unit helps identify all influencers and stakeholders.",
                "required": False,
                "follow_up": "Who has veto power over this decision?",
            },
        ],
    }

    # Demographic questions to complement the 5 Rings
    DEMOGRAPHIC_QUESTIONS = [
        {
            "id": "demo_role",
            "question": "What's your current job title and primary responsibilities?",
            "required": True,
        },
        {
            "id": "demo_company",
            "question": "What industry is your company in, and approximately how many employees?",
            "required": True,
        },
        {
            "id": "demo_experience",
            "question": "How long have you been in this role or industry?",
            "required": False,
        },
    ]

    def get_questions_for_ring(self, ring_type: RingType) -> List[Dict[str, Any]]:
        """Get all questions for a specific ring."""
        return self.RING_QUESTIONS.get(ring_type, [])

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by its ID."""
        for ring_questions in self.RING_QUESTIONS.values():
            for question in ring_questions:
                if question["id"] == question_id:
                    return question

        for question in self.DEMOGRAPHIC_QUESTIONS:
            if question["id"] == question_id:
                return question

        return None


class InterviewEngine:
    """Manages the interview flow and data collection process."""

    def __init__(self):
        self.question_bank = InterviewQuestionBank()
        self.active_sessions: Dict[str, InterviewSession] = {}

    def start_interview(self, product_context: str = "") -> Tuple[str, Dict[str, Any]]:
        """Start a new interview session."""
        session_id = str(uuid.uuid4())
        session = InterviewSession(
            session_id=session_id, current_ring=RingType.PRIORITY_INITIATIVE
        )

        # Store context for dynamic questioning
        if product_context:
            session.responses["product_context"] = product_context

        self.active_sessions[session_id] = session

        # Return first question
        first_question = self._get_next_question(session)

        logger.info(f"Started interview session {session_id}")

        return session_id, {
            "session_id": session_id,
            "question": first_question,
            "progress": self._get_progress_info(session),
            "context": "We'll explore your buying situation using Adele Revella's proven methodology. This should take about 10-15 minutes.",
        }

    def answer_question(self, session_id: str, response: str) -> Dict[str, Any]:
        """Process a response and return the next question or completion."""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Store the response
        current_question_id = self._get_current_question_id(session)
        session.add_response(current_question_id, response)

        # Check if we need a follow-up question
        follow_up = self._should_ask_follow_up(session, current_question_id, response)
        if follow_up:
            return {
                "session_id": session_id,
                "question": follow_up,
                "progress": self._get_progress_info(session),
                "is_follow_up": True,
            }

        # Move to next question or ring
        next_question = self._advance_to_next_question(session)

        if next_question:
            return {
                "session_id": session_id,
                "question": next_question,
                "progress": self._get_progress_info(session),
                "is_follow_up": False,
            }
        else:
            # Interview completed
            session.complete_session()
            return {
                "session_id": session_id,
                "completed": True,
                "message": "Interview completed! Now conducting market research to enrich your persona...",
                "progress": self._get_progress_info(session),
            }

    def get_session_data(self, session_id: str) -> Optional[InterviewSession]:
        """Get session data for persona building."""
        return self.active_sessions.get(session_id)

    def _get_next_question(self, session: InterviewSession) -> Dict[str, Any]:
        """Get the next appropriate question for the session."""
        ring_questions = self.question_bank.get_questions_for_ring(session.current_ring)

        # Find first unanswered required question
        for question in ring_questions:
            if question["id"] not in session.responses and question.get(
                "required", False
            ):
                return self._format_question(question, session.current_ring)

        # Find first unanswered optional question
        for question in ring_questions:
            if question["id"] not in session.responses:
                return self._format_question(question, session.current_ring)

        # No more questions in this ring, move to next
        return self._move_to_next_ring(session)

    def _format_question(
        self, question: Dict[str, Any], ring_type: RingType
    ) -> Dict[str, Any]:
        """Format question with ring context."""
        return {
            "id": question["id"],
            "text": question["question"],
            "context": question.get("context", ""),
            "ring": ring_type.value,
            "required": question.get("required", False),
        }

    def _get_current_question_id(self, session: InterviewSession) -> str:
        """Get the ID of the current question being answered."""
        # Simple implementation - track last question asked
        ring_questions = self.question_bank.get_questions_for_ring(session.current_ring)

        for question in ring_questions:
            if question["id"] not in session.responses:
                return question["id"]

        return f"ring_{session.current_ring.value}_complete"

    def _should_ask_follow_up(
        self, session: InterviewSession, question_id: str, response: str
    ) -> Optional[Dict[str, Any]]:
        """Determine if a follow-up question should be asked."""
        question = self.question_bank.get_question_by_id(question_id)
        if not question or not question.get("follow_up"):
            return None

        # Simple heuristic: ask follow-up if response is short or vague
        if len(response.split()) < 10:
            return {
                "id": f"{question_id}_followup",
                "text": question["follow_up"],
                "context": "Can you provide more specific details?",
                "ring": session.current_ring.value,
                "required": False,
            }

        return None

    def _advance_to_next_question(
        self, session: InterviewSession
    ) -> Optional[Dict[str, Any]]:
        """Advance to the next question or ring."""
        # Check if current ring has more questions
        next_question = self._get_next_question(session)
        if next_question.get("id") != f"ring_{session.current_ring.value}_complete":
            return next_question

        # Move to next ring
        return self._move_to_next_ring(session)

    def _move_to_next_ring(self, session: InterviewSession) -> Optional[Dict[str, Any]]:
        """Move to the next ring in the methodology."""
        ring_order = [
            RingType.PRIORITY_INITIATIVE,
            RingType.SUCCESS_FACTORS,
            RingType.PERCEIVED_BARRIERS,
            RingType.DECISION_CRITERIA,
            RingType.BUYER_JOURNEY,
        ]

        current_index = ring_order.index(session.current_ring)

        # Check if we've completed all rings
        if current_index >= len(ring_order) - 1:
            return None  # Interview complete

        # Move to next ring
        session.current_ring = ring_order[current_index + 1]
        return self._get_next_question(session)

    def _get_progress_info(self, session: InterviewSession) -> Dict[str, Any]:
        """Get progress information for the session."""
        total_rings = 5
        ring_order = [
            RingType.PRIORITY_INITIATIVE,
            RingType.SUCCESS_FACTORS,
            RingType.PERCEIVED_BARRIERS,
            RingType.DECISION_CRITERIA,
            RingType.BUYER_JOURNEY,
        ]

        current_ring_index = ring_order.index(session.current_ring)

        # Count completed questions
        total_questions = sum(
            len(self.question_bank.get_questions_for_ring(ring)) for ring in ring_order
        )
        answered_questions = len(
            [
                r
                for r in session.responses.keys()
                if not r.endswith("_followup") and r != "product_context"
            ]
        )

        return {
            "current_ring": session.current_ring.value,
            "ring_progress": f"{current_ring_index + 1}/{total_rings}",
            "question_progress": f"{answered_questions}/{total_questions}",
            "percentage": (
                round((answered_questions / total_questions) * 100, 1)
                if total_questions > 0
                else 0
            ),
        }

    def extract_demographics_from_responses(
        self, session: InterviewSession
    ) -> Demographics:
        """Extract demographic information from interview responses."""
        demographics = Demographics()

        # Extract from specific demographic questions
        if "demo_role" in session.responses:
            demographics.job_title = session.responses["demo_role"]

        if "demo_company" in session.responses:
            company_info = session.responses["demo_company"]
            # Simple parsing - in production, use more sophisticated NLP
            if "startup" in company_info.lower() or "small" in company_info.lower():
                demographics.company_size = "small"
            elif (
                "enterprise" in company_info.lower() or "large" in company_info.lower()
            ):
                demographics.company_size = "large"
            else:
                demographics.company_size = "medium"

            # Extract industry
            industries = ["fintech", "saas", "ecommerce", "healthcare", "technology"]
            for industry in industries:
                if industry in company_info.lower():
                    demographics.industry = industry
                    break

        if "demo_experience" in session.responses:
            demographics.experience_level = session.responses["demo_experience"]

        return demographics

    def get_interview_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate a summary of the interview session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return {}

        summary = {
            "session_id": session_id,
            "started_at": session.started_at.isoformat(),
            "completed_at": (
                session.completed_at.isoformat() if session.completed_at else None
            ),
            "is_completed": session.is_completed,
            "total_responses": len(session.responses),
            "rings_covered": [],
        }

        # Analyze responses by ring
        for ring_type in RingType:
            ring_questions = self.question_bank.get_questions_for_ring(ring_type)
            ring_responses = [
                q["id"] for q in ring_questions if q["id"] in session.responses
            ]

            if ring_responses:
                summary["rings_covered"].append(
                    {
                        "ring": ring_type.value,
                        "questions_answered": len(ring_responses),
                        "total_questions": len(ring_questions),
                        "completion_rate": (
                            len(ring_responses) / len(ring_questions)
                            if ring_questions
                            else 0
                        ),
                    }
                )

        return summary
