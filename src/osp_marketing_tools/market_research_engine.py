"""Market Research Engine for Interactive Buyer Persona Generator.

Implements intelligent web search with DDGS, rate limiting,
and fallback strategies based on the 5 Rings methodology.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None
    logging.warning(
        "ddgs not available. Install with: pip install ddgs"
    )

from .config import Config
from .fallback_data_provider import FallbackDataProvider
from .persona_data_structures import MarketResearchResult, RingType

logger = logging.getLogger(__name__)


class RingSpecificResearchBuilder:
    """Builds contextual research queries for each of the 5 Rings."""

    # Research query templates for each Ring
    RING_RESEARCH_TEMPLATES = {
        RingType.PRIORITY_INITIATIVE: {
            "trigger_events": [
                "{industry} trigger events driving change 2024",
                "{industry} business pressures forcing decisions",
                "{company_size} companies {industry} urgent needs",
                "why {industry} companies need {product_category} now",
            ],
            "urgency_drivers": [
                "{industry} competitive pressure trends",
                "{industry} regulatory changes 2024",
                "{industry} market disruption factors",
            ],
        },
        RingType.SUCCESS_FACTORS: {
            "business_outcomes": [
                "{industry} ROI expectations {product_category}",
                "{industry} success metrics {product_category}",
                "{company_size} {industry} performance goals",
            ],
            "success_stories": [
                "{industry} {product_category} case studies",
                "{industry} companies improved with {product_category}",
                "{product_category} success stories {industry}",
            ],
        },
        RingType.PERCEIVED_BARRIERS: {
            "common_objections": [
                "{industry} {product_category} implementation challenges",
                "{industry} concerns about {product_category}",
                "why {industry} companies hesitate {product_category}",
            ],
            "risk_factors": [
                "{industry} {product_category} security concerns",
                "{industry} integration challenges {product_category}",
                "{industry} {product_category} failure stories",
            ],
        },
        RingType.DECISION_CRITERIA: {
            "evaluation_factors": [
                "{industry} {product_category} selection criteria",
                "{industry} {product_category} feature requirements",
                "{company_size} {industry} vendor evaluation",
            ],
            "comparison_factors": [
                "{industry} {product_category} comparison checklist",
                "{industry} {product_category} RFP requirements",
            ],
        },
        RingType.BUYER_JOURNEY: {
            "research_behavior": [
                "{industry} {job_title} research sources",
                "{industry} decision making process {product_category}",
                "{industry} {product_category} evaluation timeline",
            ],
            "influencers": [
                "{industry} {product_category} decision influencers",
                "{industry} thought leaders {product_category}",
                "{job_title} {industry} trusted sources",
            ],
        },
    }

    def build_research_queries(
        self, ring_type: RingType, context: Dict[str, str]
    ) -> List[str]:
        """Build targeted research queries for a specific ring."""
        templates = self.RING_RESEARCH_TEMPLATES.get(ring_type, {})
        queries = []

        # Extract context variables
        industry = context.get("industry", "technology")
        company_size = context.get("company_size", "medium")
        job_title = context.get("job_title", "manager")
        product_category = self._normalize_product_category(context.get("product", ""))

        # Build queries from templates
        for category, template_list in templates.items():
            for template in template_list:
                try:
                    query = template.format(
                        industry=industry,
                        company_size=company_size,
                        job_title=job_title,
                        product_category=product_category,
                    )
                    queries.append(query)
                except KeyError as e:
                    logger.warning(f"Template formatting error: {e}")
                    continue

        # Limit to avoid rate limiting
        return queries[:3]  # Max 3 queries per ring

    def _normalize_product_category(self, product: str) -> str:
        """Normalize product description to a category."""
        product_lower = product.lower()

        if any(
            term in product_lower for term in ["software", "app", "platform", "tool"]
        ):
            return "software"
        elif any(
            term in product_lower for term in ["service", "consulting", "consultoria"]
        ):
            return "service"
        elif any(term in product_lower for term in ["saas", "cloud"]):
            return "SaaS"
        else:
            return product_lower or "business solution"


class AsyncRateLimiter:
    """Simple async rate limiter for web requests."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire rate limit permission."""
        async with self.lock:
            now = datetime.now()
            # Remove requests older than 1 minute
            cutoff = now.timestamp() - 60
            self.request_times = [t for t in self.request_times if t > cutoff]

            if len(self.request_times) >= self.requests_per_minute:
                # Calculate wait time
                oldest_request = min(self.request_times)
                wait_time = 60 - (now.timestamp() - oldest_request)
                if wait_time > 0:
                    logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)

            self.request_times.append(now.timestamp())


class MarketResearchEngine:
    """Orchestrates market research with web search and fallback strategies."""

    def __init__(self):
        self.rate_limiter = AsyncRateLimiter(Config.RATE_LIMIT_REQUESTS_PER_MINUTE)
        self.research_builder = RingSpecificResearchBuilder()
        self.fallback_provider = FallbackDataProvider()
        self.search_engine = DDGS() if DDGS else None

        if not self.search_engine:
            logger.warning(
                "DDGS search not available. Will use fallback data only."
            )

    async def conduct_batch_research(
        self, persona_context: Dict[str, str]
    ) -> Dict[str, MarketResearchResult]:
        """Conduct research for all rings in batch to respect rate limits."""

        logger.info("Starting batch market research")
        research_tasks = []

        # Build research tasks for each ring
        for ring_type in RingType:
            queries = self.research_builder.build_research_queries(
                ring_type, persona_context
            )
            for i, query in enumerate(queries):
                task_id = f"{ring_type.value}_{i}"
                research_tasks.append(
                    {
                        "task_id": task_id,
                        "ring_type": ring_type,
                        "query": query,
                        "context": persona_context,
                    }
                )

        # Execute research tasks with rate limiting
        results = {}
        for task in research_tasks:
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire()

                # Perform search
                search_results = await self._safe_search(task["query"], max_results=3)

                results[task["task_id"]] = MarketResearchResult(
                    query=task["query"],
                    results=search_results,
                    source="ddgs" if search_results else "fallback",
                    success=bool(search_results),
                )

                logger.info(f"Research completed for: {task['query'][:50]}...")

            except Exception as e:
                # Use fallback data on error
                fallback_data = self.fallback_provider.get_generic_data(task["query"])

                results[task["task_id"]] = MarketResearchResult(
                    query=task["query"],
                    results=fallback_data,
                    source="fallback",
                    success=False,
                    error_message=str(e),
                )

                logger.warning(
                    f"Research failed for {task['query']}, using fallback: {str(e)}"
                )

        logger.info(f"Batch research completed. {len(results)} queries processed.")
        return results

    async def _safe_search(self, query: str, max_results: int = 5) -> List[str]:
        """Search with multiple fallback strategies."""
        if not self.search_engine:
            return self.fallback_provider.get_generic_data(query)

        try:
            # Strategy 1: DDGS search
            results = self.search_engine.text(query, max_results=max_results)
            if results:
                return [r.get("body", "")[:200] for r in results if r.get("body")]

        except Exception as e1:
            logger.warning(f"DDGS search failed: {e1}")

            try:
                # Strategy 2: Simplified query
                simplified_query = self._simplify_query(query)
                results = self.search_engine.text(simplified_query, max_results=3)
                if results:
                    return [r.get("body", "")[:200] for r in results if r.get("body")]

            except Exception as e2:
                logger.warning(f"Simplified search failed: {e2}")

        # Strategy 3: Complete fallback
        return self.fallback_provider.get_generic_data(query)

    def _simplify_query(self, query: str) -> str:
        """Simplify query to improve success chances."""
        # Remove years, complex terms, etc.
        simplified = query.replace("2024", "").replace("2025", "")
        simplified = simplified.replace("brasil", "brazil")

        # Take only first 3 words
        words = simplified.split()[:3]
        return " ".join(words)

    async def research_ring_specific(
        self, ring_type: RingType, context: Dict[str, str]
    ) -> Dict[str, MarketResearchResult]:
        """Conduct research for a specific ring only."""
        queries = self.research_builder.build_research_queries(ring_type, context)
        results = {}

        for i, query in enumerate(queries):
            task_id = f"{ring_type.value}_{i}"

            try:
                await self.rate_limiter.acquire()
                search_results = await self._safe_search(query, max_results=3)

                results[task_id] = MarketResearchResult(
                    query=query,
                    results=search_results,
                    source="ddgs" if search_results else "fallback",
                    success=bool(search_results),
                )

            except Exception as e:
                fallback_data = self.fallback_provider.get_generic_data(query)
                results[task_id] = MarketResearchResult(
                    query=query,
                    results=fallback_data,
                    source="fallback",
                    success=False,
                    error_message=str(e),
                )

        return results

    def get_research_summary(
        self, research_results: Dict[str, MarketResearchResult]
    ) -> Dict[str, Any]:
        """Generate summary of research results."""
        total_queries = len(research_results)
        successful_queries = sum(1 for r in research_results.values() if r.success)
        fallback_queries = total_queries - successful_queries

        sources = {}
        for result in research_results.values():
            sources[result.source] = sources.get(result.source, 0) + 1

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "fallback_queries": fallback_queries,
            "success_rate": (
                (successful_queries / total_queries * 100) if total_queries > 0 else 0
            ),
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
        }
