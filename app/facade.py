"""
RTKFacade — single entry point for all red team orchestration.
Tenacity wraps on all external calls. Async parallel execution.
All providers registered at startup. Multi-vector campaign support.
"""

import asyncio
import re
from typing import Optional

import tenacity
from langchain_anthropic import ChatAnthropic
from tenacity import stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.models import (
    AttackResult,
    AttackTool,
    CampaignConfig,
    OrchestratorResult,
)
from app.providers.base import AttackProvider
from app.providers.crewai_provider import CrewAIProvider
from app.providers.deepteam_provider import DeepTeamProvider
from app.providers.garak_provider import GarakProvider
from app.providers.promptfoo_provider import PromptfooProvider
from app.providers.pyrit_provider import PyRITProvider
from app.providers.scorer_generator import ScorerGenerator

logger = get_logger("facade")


class RTKFacade:
    """
    Swappable facade for RTK-1 attack orchestration.
    All providers registered at startup.
    Tenacity on all external calls.
    Parallel execution via asyncio.gather.
    """

    def __init__(
        self,
        provider: Optional[AttackProvider] = None,
        llm: Optional[ChatAnthropic] = None,
    ):
        self._llm = llm or ChatAnthropic(
            model=settings.default_model,
            temperature=settings.default_temperature,
            max_tokens=settings.default_max_tokens,
            anthropic_api_key=settings.anthropic_api_key,
        )

        # Register all providers
        pyrit = PyRITProvider(llm=self._llm)
        garak = GarakProvider()
        deepteam = DeepTeamProvider(llm=self._llm)
        promptfoo = PromptfooProvider()
        crewai = CrewAIProvider(llm=self._llm)

        self._providers: dict[str, AttackProvider] = {
            "pyrit": pyrit,
            "garak": garak,
            "deepteam": deepteam,
            "promptfoo": promptfoo,
            "crewai": crewai,
        }

        self._provider = provider or pyrit
        self._scorer_generator = ScorerGenerator(llm=self._llm)

        available = [name for name, p in self._providers.items() if p.is_available()]
        logger.info("facade_initialized", available_providers=available)

    def get_provider(self, tool_name: str) -> AttackProvider:
        """Get provider by name, fallback to PyRIT."""
        provider = self._providers.get(tool_name)
        if not provider or not provider.is_available():
            logger.warning(
                "provider_unavailable_fallback", requested=tool_name, fallback="pyrit"
            )
            return self._providers["pyrit"]
        return provider

    def register_provider(self, provider: AttackProvider) -> None:
        self._providers[provider.tool_name] = provider
        logger.info("provider_registered", tool=provider.tool_name)

    @tenacity.retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_scorer_with_retry(self, config: CampaignConfig):
        return await self._scorer_generator.generate(
            goal=config.goal,
            customer_success_metrics=config.customer_success_metrics,
            target_model=config.target_model,
        )

    @tenacity.retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=3, max=15),
        reraise=True,
    )
    async def _run_provider_with_retry(
        self,
        provider: AttackProvider,
        config: CampaignConfig,
        scorer_config,
    ) -> list[AttackResult]:
        return await provider.run_campaign(config=config, scorer_config=scorer_config)

    async def run_campaign(self, config: CampaignConfig) -> OrchestratorResult:
        """Execute full attack campaign with retry logic."""
        logger.info(
            "campaign_started", campaign_id=config.campaign_id, goal=config.goal
        )

        provider = self.get_provider(config.tool.value)
        scorer_config = await self._generate_scorer_with_retry(config)
        logger.info("scorer_generated", objective=scorer_config.objective_summary)

        results = await self._run_provider_with_retry(provider, config, scorer_config)

        total = len(results)
        successful = sum(1 for r in results if r.success)
        asr = round((successful / total) * 100, 2) if total > 0 else 0.0

        logger.info("campaign_completed", campaign_id=config.campaign_id, asr=asr)

        return OrchestratorResult(
            campaign_id=config.campaign_id,
            status="completed",
            vector=config.vector,
            tool_used=AttackTool(provider.tool_name),
            target_model=config.target_model,
            goal=config.goal,
            customer_success_metrics=config.customer_success_metrics,
            total_sequences=total,
            successful_sequences=successful,
            asr=asr,
            results=results,
        )

    async def run_multi_vector_campaign(
        self,
        config: CampaignConfig,
        vectors: list[str] = None,
    ) -> dict:
        """
        Objective 19 — Multi-vector unified campaign.
        Runs PyRIT (crescendo) + Garak (broad scan) + DeepTeam (structured)
        in parallel and aggregates into one unified report.
        """
        vectors = vectors or ["pyrit", "garak", "deepteam"]
        logger.info("multi_vector_started", vectors=vectors)

        scorer_config = await self._generate_scorer_with_retry(config)

        async def run_vector(tool_name: str) -> OrchestratorResult:
            provider = self.get_provider(tool_name)
            vector_config = config.model_copy(update={"tool": AttackTool(tool_name)})
            try:
                results = await self._run_provider_with_retry(
                    provider, vector_config, scorer_config
                )
                total = len(results)
                successful = sum(1 for r in results if r.success)
                asr = round((successful / total) * 100, 2) if total > 0 else 0.0
                return OrchestratorResult(
                    campaign_id=config.campaign_id,
                    status="completed",
                    vector=config.vector,
                    tool_used=AttackTool(tool_name),
                    target_model=config.target_model,
                    goal=config.goal,
                    customer_success_metrics=config.customer_success_metrics,
                    total_sequences=total,
                    successful_sequences=successful,
                    asr=asr,
                    results=results,
                )
            except Exception as e:
                logger.error("vector_failed", tool=tool_name, error=str(e))
                return None

        vector_results = await asyncio.gather(
            *[run_vector(v) for v in vectors],
            return_exceptions=False,
        )

        valid_results = [r for r in vector_results if r is not None]
        all_results = []
        for r in valid_results:
            all_results.extend(r.results)

        total = len(all_results)
        successful = sum(1 for r in all_results if r.success)
        combined_asr = round((successful / total) * 100, 2) if total > 0 else 0.0

        logger.info(
            "multi_vector_complete",
            vectors=len(valid_results),
            combined_asr=combined_asr,
        )

        return {
            "campaign_id": config.campaign_id,
            "goal": config.goal,
            "target_model": config.target_model,
            "vectors_run": [r.tool_used.value for r in valid_results],
            "combined_asr": combined_asr,
            "per_vector": [
                {
                    "tool": r.tool_used.value,
                    "asr": r.asr,
                    "sequences": r.total_sequences,
                    "successful": r.successful_sequences,
                }
                for r in valid_results
            ],
            "all_results": all_results,
        }

    async def run_parallel_campaigns(
        self,
        configs: list[CampaignConfig],
    ) -> list[OrchestratorResult]:
        """Run multiple campaigns in parallel via asyncio.gather."""
        logger.info("parallel_campaigns_started", count=len(configs))

        scorer_tasks = [self._generate_scorer_with_retry(c) for c in configs]
        scorer_configs = await asyncio.gather(*scorer_tasks, return_exceptions=True)

        campaign_tasks = []
        for config, scorer_config in zip(configs, scorer_configs):
            if isinstance(scorer_config, Exception):
                logger.warning("scorer_failed", campaign_id=config.campaign_id)
                continue
            provider = self.get_provider(config.tool.value)
            campaign_tasks.append(
                self._run_provider_with_retry(provider, config, scorer_config)
            )

        all_results = await asyncio.gather(*campaign_tasks, return_exceptions=True)

        orchestrator_results = []
        for config, results in zip(configs, all_results):
            if isinstance(results, Exception):
                logger.error(
                    "campaign_failed",
                    campaign_id=config.campaign_id,
                    error=str(results),
                )
                continue
            total = len(results)
            successful = sum(1 for r in results if r.success)
            asr = round((successful / total) * 100, 2) if total > 0 else 0.0
            orchestrator_results.append(
                OrchestratorResult(
                    campaign_id=config.campaign_id,
                    status="completed",
                    vector=config.vector,
                    tool_used=AttackTool(config.tool.value),
                    target_model=config.target_model,
                    goal=config.goal,
                    customer_success_metrics=config.customer_success_metrics,
                    total_sequences=total,
                    successful_sequences=successful,
                    asr=asr,
                    results=results,
                )
            )

        logger.info("parallel_campaigns_completed", count=len(orchestrator_results))
        return orchestrator_results

    @tenacity.retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def ainvoke(self, prompt: str):
        """LLM pass-through with tenacity retry."""
        response = await self._llm.ainvoke(prompt)
        raw = response.content.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            response = response.model_copy(update={"content": match.group()})
        return response


def get_facade(provider: Optional[AttackProvider] = None) -> RTKFacade:
    return RTKFacade(provider=provider)


facade = get_facade()
