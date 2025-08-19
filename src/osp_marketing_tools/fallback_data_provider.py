"""Fallback Data Provider for Interactive Buyer Persona Generator.

Provides rich, industry-specific fallback data when web research fails,
based on Adele Revella's 5 Rings of Buying Insight methodology.
"""

import logging
from typing import Any, Dict, List, Optional

from .persona_data_structures import RingType

logger = logging.getLogger(__name__)


class FallbackDataProvider:
    """Provides structured fallback data when market research fails."""

    # Industry-specific fallback data organized by the 5 Rings
    RING_BASED_FALLBACKS = {
        "fintech": {
            RingType.PRIORITY_INITIATIVE: {
                "trigger_events": [
                    "Regulatory compliance pressure (Open Banking, PCI DSS)",
                    "Customer demand for digital-first experiences",
                    "Competitive threat from neobanks",
                    "Cost pressure to reduce manual processes",
                    "Security incident or fraud concerns",
                ],
                "urgency_drivers": [
                    "Regulatory deadline approaching",
                    "Customer churn to competitors",
                    "Rising operational costs",
                    "Board/investor pressure for digital transformation",
                ],
            },
            RingType.SUCCESS_FACTORS: {
                "tangible_outcomes": [
                    "Reduce transaction processing time by 60%",
                    "Decrease customer acquisition cost by 40%",
                    "Improve Net Promoter Score by 25 points",
                    "Reduce operational costs by 30%",
                ],
                "intangible_outcomes": [
                    "Enhanced brand reputation as innovation leader",
                    "Improved customer trust and loyalty",
                    "Employee satisfaction with modern tools",
                    "Competitive advantage in digital banking",
                ],
            },
            RingType.PERCEIVED_BARRIERS: {
                "risk_concerns": [
                    "Data security and privacy compliance",
                    "Integration complexity with legacy systems",
                    "Regulatory approval process delays",
                    "Customer adoption resistance",
                ],
                "past_experiences": [
                    "Previous fintech vendor disappointed on security",
                    "Integration project went over budget/timeline",
                    "Customer complaints about app usability",
                ],
            },
            RingType.DECISION_CRITERIA: {
                "must_have_features": [
                    "SOC 2 Type II and PCI DSS compliance",
                    "Real-time transaction processing",
                    "API-first architecture for integrations",
                    "Multi-factor authentication",
                ],
                "evaluation_factors": [
                    "Security track record and certifications",
                    "Integration complexity and timeline",
                    "Total cost of ownership over 3 years",
                    "Vendor financial stability and support",
                ],
            },
            RingType.BUYER_JOURNEY: {
                "research_sources": [
                    "Industry publications (American Banker, Finextra)",
                    "Peer recommendations from fintech conferences",
                    "Gartner/Forrester research reports",
                    "LinkedIn professional networks",
                ],
                "decision_timeline": "3-6 months (due to regulatory considerations)",
                "approval_process": "Technical review → Security audit → Executive approval → Board notification",
            },
        },
        "saas": {
            RingType.PRIORITY_INITIATIVE: {
                "trigger_events": [
                    "Scaling challenges with current system",
                    "Customer complaints about user experience",
                    "Competitive feature gap identified",
                    "Team productivity bottlenecks",
                    "Security or compliance requirements",
                ],
                "urgency_drivers": [
                    "Upcoming product launch deadline",
                    "Customer renewal negotiations",
                    "Team growth requiring better tools",
                    "Investor/board pressure for efficiency",
                ],
            },
            RingType.SUCCESS_FACTORS: {
                "tangible_outcomes": [
                    "Increase team productivity by 50%",
                    "Reduce customer support tickets by 35%",
                    "Improve feature delivery velocity by 40%",
                    "Decrease system downtime by 80%",
                ],
                "intangible_outcomes": [
                    "Improved team satisfaction and retention",
                    "Enhanced customer experience and loyalty",
                    "Competitive advantage in feature development",
                    "Better work-life balance for technical team",
                ],
            },
            RingType.PERCEIVED_BARRIERS: {
                "risk_concerns": [
                    "Migration complexity and potential downtime",
                    "Learning curve for team adoption",
                    "Integration with existing tech stack",
                    "Vendor lock-in concerns",
                ],
                "past_experiences": [
                    "Previous SaaS tool abandoned due to poor UX",
                    "Integration project took longer than expected",
                    "Team resistance to changing familiar tools",
                ],
            },
            RingType.DECISION_CRITERIA: {
                "must_have_features": [
                    "REST API for custom integrations",
                    "SSO integration with existing identity provider",
                    "Role-based access control",
                    "99.9% uptime SLA guarantee",
                ],
                "evaluation_factors": [
                    "Ease of implementation and onboarding",
                    "Quality of customer support and documentation",
                    "Scalability to support team growth",
                    "Total cost including training and setup",
                ],
            },
            RingType.BUYER_JOURNEY: {
                "research_sources": [
                    "Product Hunt and tech community recommendations",
                    "Developer communities (Stack Overflow, Reddit)",
                    "YouTube demos and tutorial videos",
                    "Free trials and proof-of-concept testing",
                ],
                "decision_timeline": "2-8 weeks (faster for smaller tools)",
                "approval_process": "Team lead evaluation → Technical proof of concept → Budget approval → Implementation",
            },
        },
        "ecommerce": {
            RingType.PRIORITY_INITIATIVE: {
                "trigger_events": [
                    "Seasonal traffic overload crashed website",
                    "Cart abandonment rate increased significantly",
                    "Competitor launched superior mobile experience",
                    "Customer complaints about checkout process",
                    "Payment processing fees becoming prohibitive",
                ],
                "urgency_drivers": [
                    "Peak season (Black Friday, holidays) approaching",
                    "Customer acquisition cost rising",
                    "Competitor gaining market share",
                    "Revenue growth stalling",
                ],
            },
            RingType.SUCCESS_FACTORS: {
                "tangible_outcomes": [
                    "Increase conversion rate by 25%",
                    "Reduce cart abandonment by 40%",
                    "Improve mobile checkout completion by 60%",
                    "Decrease page load time by 50%",
                ],
                "intangible_outcomes": [
                    "Better customer satisfaction scores",
                    "Enhanced brand perception",
                    "Improved team confidence in platform",
                    "Competitive advantage in user experience",
                ],
            },
            RingType.PERCEIVED_BARRIERS: {
                "risk_concerns": [
                    "Migration disrupting sales during peak season",
                    "SEO rankings loss during platform transition",
                    "Customer data migration complexities",
                    "Payment gateway integration issues",
                ],
                "past_experiences": [
                    "Previous platform migration caused revenue drop",
                    "E-commerce vendor oversold capabilities",
                    "Integration with existing tools was problematic",
                ],
            },
            RingType.DECISION_CRITERIA: {
                "must_have_features": [
                    "Mobile-first responsive design",
                    "Multiple payment gateway support",
                    "Inventory management integration",
                    "SEO-friendly URL structure",
                ],
                "evaluation_factors": [
                    "Platform scalability for traffic spikes",
                    "Third-party app ecosystem",
                    "Migration support and timeline",
                    "Monthly transaction fees and limits",
                ],
            },
            RingType.BUYER_JOURNEY: {
                "research_sources": [
                    "E-commerce industry blogs (Shopify, BigCommerce)",
                    "Peer recommendations from merchant communities",
                    "Comparison sites and review platforms",
                    "Social media groups and forums",
                ],
                "decision_timeline": "1-3 months (urgent during off-season)",
                "approval_process": "Technical evaluation → Cost-benefit analysis → Stakeholder buy-in → Implementation planning",
            },
        },
        "healthtech": {
            RingType.PRIORITY_INITIATIVE: {
                "trigger_events": [
                    "HIPAA compliance audit findings",
                    "Patient satisfaction scores declining",
                    "Staff burnout from manual processes",
                    "Competitive pressure from digital-native providers",
                    "Insurance reimbursement changes",
                ],
                "urgency_drivers": [
                    "Regulatory compliance deadline",
                    "Patient retention declining",
                    "Staff turnover increasing",
                    "Board pressure for digital transformation",
                ],
            },
            RingType.SUCCESS_FACTORS: {
                "tangible_outcomes": [
                    "Reduce patient wait times by 45%",
                    "Improve appointment booking efficiency by 70%",
                    "Decrease administrative costs by 35%",
                    "Increase patient satisfaction scores by 30%",
                ],
                "intangible_outcomes": [
                    "Better work-life balance for healthcare staff",
                    "Enhanced patient trust and loyalty",
                    "Improved clinical decision-making capabilities",
                    "Competitive advantage in patient experience",
                ],
            },
            RingType.PERCEIVED_BARRIERS: {
                "risk_concerns": [
                    "HIPAA compliance and data security",
                    "Integration with existing EMR systems",
                    "Staff training and adoption challenges",
                    "Patient privacy and consent management",
                ],
                "past_experiences": [
                    "Previous healthtech vendor had security breach",
                    "EMR integration project took 18+ months",
                    "Staff complained about system complexity",
                ],
            },
            RingType.DECISION_CRITERIA: {
                "must_have_features": [
                    "HIPAA compliance certification",
                    "HL7 FHIR integration capabilities",
                    "Role-based access control",
                    "Audit logging and reporting",
                ],
                "evaluation_factors": [
                    "Healthcare industry experience",
                    "Security certifications and track record",
                    "Integration complexity and support",
                    "Training and onboarding program quality",
                ],
            },
            RingType.BUYER_JOURNEY: {
                "research_sources": [
                    "Healthcare IT publications (Healthcare IT News)",
                    "Medical professional associations",
                    "Industry conferences (HIMSS, CHIME)",
                    "Peer networks and medical societies",
                ],
                "decision_timeline": "6-12 months (due to regulatory requirements)",
                "approval_process": "Clinical review → IT security assessment → Compliance approval → Board approval → Implementation",
            },
        },
    }

    # Generic fallback data for unknown industries
    GENERIC_FALLBACKS = {
        RingType.PRIORITY_INITIATIVE: {
            "trigger_events": [
                "Competitive pressure in the market",
                "Customer demands for better service",
                "Operational inefficiencies identified",
                "Cost reduction requirements",
                "Technology modernization needs",
            ],
            "urgency_drivers": [
                "Market share decline",
                "Customer satisfaction issues",
                "Rising operational costs",
                "Management directive for improvement",
            ],
        },
        RingType.SUCCESS_FACTORS: {
            "tangible_outcomes": [
                "Increase operational efficiency by 30%",
                "Reduce costs by 20%",
                "Improve customer satisfaction by 25%",
                "Increase revenue by 15%",
            ],
            "intangible_outcomes": [
                "Better team morale and productivity",
                "Enhanced brand reputation",
                "Competitive advantage",
                "Improved work environment",
            ],
        },
        RingType.PERCEIVED_BARRIERS: {
            "risk_concerns": [
                "Implementation complexity",
                "Change management challenges",
                "Budget constraints",
                "Technology integration issues",
            ],
            "past_experiences": [
                "Previous vendor disappointed on delivery",
                "Implementation took longer than expected",
                "Team resistance to new tools",
            ],
        },
        RingType.DECISION_CRITERIA: {
            "must_have_features": [
                "Ease of use and adoption",
                "Reliable customer support",
                "Scalable architecture",
                "Cost-effective pricing",
            ],
            "evaluation_factors": [
                "Vendor reputation and stability",
                "Implementation timeline",
                "Total cost of ownership",
                "Training and support quality",
            ],
        },
        RingType.BUYER_JOURNEY: {
            "research_sources": [
                "Industry publications and blogs",
                "Peer recommendations",
                "Online reviews and comparisons",
                "Professional networks",
            ],
            "decision_timeline": "2-4 months (typical for business tools)",
            "approval_process": "Evaluation → Budget approval → Stakeholder buy-in → Implementation",
        },
    }

    def get_ring_fallback(
        self,
        ring_type: RingType,
        industry: str = "generic",
        company_size: str = "medium",
    ) -> Dict[str, Any]:
        """Get fallback data for a specific ring and industry."""
        industry_lower = industry.lower()

        # Try to get industry-specific data
        industry_data = self.RING_BASED_FALLBACKS.get(industry_lower, {})
        ring_data = industry_data.get(ring_type)

        if ring_data:
            logger.info(f"Using {industry} fallback data for {ring_type.value}")
            return self._customize_by_company_size(ring_data, company_size)

        # Fall back to generic data
        generic_data = self.GENERIC_FALLBACKS.get(ring_type, {})
        logger.info(f"Using generic fallback data for {ring_type.value}")
        return self._customize_by_company_size(generic_data, company_size)

    def _customize_by_company_size(
        self, data: Dict[str, Any], company_size: str
    ) -> Dict[str, Any]:
        """Customize fallback data based on company size."""
        customized = data.copy()

        size_lower = company_size.lower()

        # Adjust metrics and expectations based on company size
        if "tangible_outcomes" in customized:
            if size_lower in ["startup", "small"]:
                # Smaller companies often have higher percentage targets
                customized["tangible_outcomes"] = [
                    outcome.replace("30%", "50%")
                    .replace("20%", "35%")
                    .replace("25%", "40%")
                    for outcome in customized["tangible_outcomes"]
                ]
            elif size_lower in ["enterprise", "large"]:
                # Larger companies often have more conservative targets
                customized["tangible_outcomes"] = [
                    outcome.replace("50%", "25%")
                    .replace("40%", "20%")
                    .replace("30%", "15%")
                    for outcome in customized["tangible_outcomes"]
                ]

        # Adjust timeline based on company size
        if "decision_timeline" in customized:
            if size_lower in ["startup", "small"]:
                customized["decision_timeline"] = (
                    customized["decision_timeline"]
                    .replace("3-6 months", "1-3 months")
                    .replace("6-12 months", "3-6 months")
                )
            elif size_lower in ["enterprise", "large"]:
                customized["decision_timeline"] = (
                    customized["decision_timeline"]
                    .replace("1-3 months", "3-6 months")
                    .replace("2-4 months", "4-8 months")
                )

        return customized

    def get_generic_data(self, query: str) -> List[str]:
        """Get generic fallback data for a search query."""
        query_lower = query.lower()

        # Simple keyword matching for basic fallback
        if any(word in query_lower for word in ["market", "industry", "trends"]):
            return [
                "Industry growth expected to continue at 15-20% annually",
                "Digital transformation driving market consolidation",
                "Customer expectations rising for seamless experiences",
            ]

        if any(word in query_lower for word in ["competition", "competitors"]):
            return [
                "Market dominated by 3-5 major players",
                "New entrants focusing on niche specialization",
                "Price competition intensifying in commodity segments",
            ]

        if any(word in query_lower for word in ["technology", "innovation"]):
            return [
                "AI and automation becoming table stakes",
                "Cloud-first architecture now standard",
                "API-first approach enabling faster integrations",
            ]

        # Default fallback
        return [
            "Industry best practices emphasize customer-centric approaches",
            "Digital-first strategies showing highest ROI",
            "Change management critical for successful implementations",
        ]

    def get_industry_list(self) -> List[str]:
        """Get list of supported industries."""
        return list(self.RING_BASED_FALLBACKS.keys())

    def is_industry_supported(self, industry: str) -> bool:
        """Check if industry has specific fallback data."""
        return industry.lower() in self.RING_BASED_FALLBACKS
