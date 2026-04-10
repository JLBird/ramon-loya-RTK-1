"""
RTK-1 Multi-Vector Provider — runs PyRIT + RAG injection + tool abuse
in parallel and returns unified results with cross-vector ASR analysis.
"""

import asyncio
from typing import List

from langchain_anthropic import ChatAnthropic

from app.core.logging import get_logger
from app.domain.models import AttackResult, CampaignConfig
from app.providers.base import AttackProvider
from app.providers.pyrit_provider import PyRITProvider
from app.providers.rag_injection_provider import RAGInjectionProvider
from app.providers.scorer_generator import ScorerConfig
from app.providers.tool_abuse_provider import ToolAbuseProvider

logger = get_logger("multi_vector_provider")


class MultiVectorProvider(AttackProvider):
    """
    Runs multiple attack vectors in parallel.
    Returns unified result set with per-vector breakdown.
    """

    def __init__(self, llm: ChatAnthropic):
        self._llm = llm
        self._pyrit = PyRITProvider(llm=llm)
        self._rag = RAGInjectionProvider(llm=llm)
        self._tool_abuse = ToolAbuseProvider(llm=llm)
        logger.info(
            "multi_vector_provider_ready",
            vectors=["pyrit", "rag_injection", "tool_abuse"],
        )

    @property
    def tool_name(self) -> str:
        return "multi_vector"

    def is_available(self) -> bool:
        return True

    async def run_campaign(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:
        """Run all vectors in parallel via asyncio.gather."""
        logger.info("multi_vector_campaign_started", goal=config.goal)

        pyrit_task = self._pyrit.run_campaign(config, scorer_config)
        rag_task = self._rag.run_campaign(config, scorer_config)
        tool_task = self._tool_abuse.run_campaign(config, scorer_config)

        all_results = await asyncio.gather(
            pyrit_task,
            rag_task,
            tool_task,
            return_exceptions=True,
        )

        combined = []
        vector_names = ["pyrit", "rag_injection", "tool_abuse"]
        for vector_name, results in zip(vector_names, all_results):
            if isinstance(results, Exception):
                logger.error("vector_failed", vector=vector_name, error=str(results))
                continue
            successful = sum(1 for r in results if r.success)
            asr = round((successful / len(results)) * 100, 2) if results else 0.0
            logger.info(
                "vector_complete", vector=vector_name, total=len(results), asr=asr
            )
            combined.extend(results)

        total = len(combined)
        successful_total = sum(1 for r in combined if r.success)
        overall_asr = round((successful_total / total) * 100, 2) if total > 0 else 0.0
        logger.info(
            "multi_vector_campaign_complete",
            total=total,
            successful=successful_total,
            overall_asr=overall_asr,
        )
        return combined
