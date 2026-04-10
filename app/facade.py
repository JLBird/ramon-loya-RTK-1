"""
RTKFacade — single entry point for all red team orchestration.
Tenacity wraps on all external calls. Async parallel execution.
All 5 providers registered at init. No raw provider objects above this layer.
"""

import asyncio
from typing import List, Optional

import tenacity
from langchain_anthropic import ChatAnthropic
from tenacity import stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.models import (
    AttackTool,
    CampaignConfig,
    OrchestratorResult,
)
from app.providers.base import AttackProvider
from app.providers.pyrit_provider import PyRITProvider
from app.providers.scorer_generator import ScorerGenerator

logger = get_logger("facade")


class RTKFacade:
    """
    Swappable facade for RTK-1 attack orchestration.
    All external calls wrapped with tenacity retry logic.
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

        # Primary provider
        self._provider = provider or PyRITProvider(llm=self._llm)
        self._scorer_generator = ScorerGenerator(llm=self._llm)

        # Provider registry — all available tools
        self._providers: dict[str, AttackProvider] = {
            self._provider.tool_name: self._provider,
        }

        # Register additional providers with safe fallbacks
        self._register_optional_providers()

        available = list(self._providers.keys())
        logger.info(
            "facade_initialized", available_providers=available, component="facade"
        )

    def _register_optional_providers(self) -> None:
        """Register all optional providers. Each fails silently if unavailable."""

        # Garak
        try:
            from app.providers.garak_provider import GarakProvider

            garak = GarakProvider(llm=self._llm)
            if garak.is_available():
                self._providers["garak"] = garak
        except Exception as e:
            logger.warning("garak_registration_failed", error=str(e))

        # DeepTeam
        try:
            from app.providers.deepteam_provider import DeepTeamProvider

            deepteam = DeepTeamProvider(llm=self._llm)
            if deepteam.is_available():
                self._providers["deepteam"] = deepteam
        except Exception as e:
            logger.warning("deepteam_registration_failed", error=str(e))

        # promptfoo
        try:
            from app.providers.promptfoo_provider import PromptfooProvider

            promptfoo = PromptfooProvider(llm=self._llm)
            if promptfoo.is_available():
                self._providers["promptfoo"] = promptfoo
        except Exception as e:
            logger.warning("promptfoo_registration_failed", error=str(e))

        # CrewAI
        try:
            from app.providers.crewai_provider import CrewAIProvider

            crewai = CrewAIProvider(llm=self._llm)
            if crewai.is_available():
                self._providers["crewai"] = crewai
        except Exception as e:
            logger.warning("crewai_registration_failed", error=str(e))

        # RAG Injection
        try:
            from app.providers.rag_injection_provider import RAGInjectionProvider

            rag = RAGInjectionProvider(llm=self._llm)
            if rag.is_available():
                self._providers["rag_injection"] = rag
        except Exception as e:
            logger.warning("rag_injection_registration_failed", error=str(e))

        # Tool Abuse
        try:
            from app.providers.tool_abuse_provider import ToolAbuseProvider

            tool_abuse = ToolAbuseProvider(llm=self._llm)
            if tool_abuse.is_available():
                self._providers["tool_abuse"] = tool_abuse
        except Exception as e:
            logger.warning("tool_abuse_registration_failed", error=str(e))

        # Multi-Vector
        try:
            from app.providers.multi_vector_provider import MultiVectorProvider

            multi = MultiVectorProvider(llm=self._llm)
            if multi.is_available():
                self._providers["multi_vector"] = multi
        except Exception as e:
            logger.warning("multi_vector_registration_failed", error=str(e))

    def register_provider(self, provider: AttackProvider) -> None:
        """Register an additional provider at runtime."""
        self._providers[provider.tool_name] = provider
        logger.info("provider_registered", tool=provider.tool_name)

    def get_provider(self, tool_name: str) -> Optional[AttackProvider]:
        """Get a specific provider by tool name."""
        return self._providers.get(tool_name)

    # ========================
    # TENACITY-WRAPPED CALLS
    # ========================

    @tenacity.retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_scorer_with_retry(self, config: CampaignConfig):
        """Scorer generation with tenacity retry."""
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
    ):
        """Provider campaign execution with tenacity retry."""
        return await provider.run_campaign(config=config, scorer_config=scorer_config)

    # ========================
    # SINGLE CAMPAIGN
    # ========================

    async def run_campaign(self, config: CampaignConfig) -> OrchestratorResult:
        """
        Execute a full attack campaign with retry logic.
        Returns clean OrchestratorResult — no raw provider objects.
        """
        logger.info(
            "campaign_started",
            campaign_id=config.campaign_id,
            goal=config.goal,
            vector=config.vector.value,
        )

        scorer_config = await self._generate_scorer_with_retry(config)
        logger.info(
            "scorer_generated",
            objective=scorer_config.objective_summary,
        )

        # Select provider — use tool specified in config if available
        provider = self._providers.get(config.tool.value, self._provider)

        results = await self._run_provider_with_retry(provider, config, scorer_config)

        total = len(results)
        successful = sum(1 for r in results if r.success)
        asr = round((successful / total) * 100, 2) if total > 0 else 0.0

        logger.info(
            "campaign_completed",
            campaign_id=config.campaign_id,
            total=total,
            successful=successful,
            asr=asr,
        )

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

    # ========================
    # PARALLEL CAMPAIGNS (Objective 7)
    # ========================

    async def run_parallel_campaigns(
        self,
        configs: List[CampaignConfig],
    ) -> List[OrchestratorResult]:
        """
        Run multiple campaigns in parallel via asyncio.gather.
        Used for multi-model comparison and multi-vector campaigns.
        """
        logger.info("parallel_campaigns_started", count=len(configs))

        scorer_tasks = [self._generate_scorer_with_retry(c) for c in configs]
        scorer_configs = await asyncio.gather(*scorer_tasks, return_exceptions=True)

        campaign_tasks = []
        valid_configs = []
        for config, scorer_config in zip(configs, scorer_configs):
            if isinstance(scorer_config, Exception):
                logger.warning(
                    "scorer_failed",
                    campaign_id=config.campaign_id,
                    error=str(scorer_config),
                )
                continue
            provider = self._providers.get(config.tool.value, self._provider)
            campaign_tasks.append(
                self._run_provider_with_retry(provider, config, scorer_config)
            )
            valid_configs.append((config, scorer_config))

        all_results = await asyncio.gather(*campaign_tasks, return_exceptions=True)

        orchestrator_results = []
        for (config, scorer_config), results in zip(valid_configs, all_results):
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
            provider = self._providers.get(config.tool.value, self._provider)
            orchestrator_results.append(
                OrchestratorResult(
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
            )

        logger.info(
            "parallel_campaigns_completed",
            count=len(orchestrator_results),
        )
        return orchestrator_results

    # ========================
    # LLM PASS-THROUGH (Objective 10)
    # ========================

    @tenacity.retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def ainvoke(self, prompt: str):
        """LLM pass-through with tenacity retry. Used by orchestrator nodes."""
        return await self._llm.ainvoke(prompt)

    # ========================
    # PROVIDER STATUS
    # ========================

    def available_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())

    def provider_status(self) -> dict:
        """Health check for all providers."""
        return {
            name: provider.is_available() for name, provider in self._providers.items()
        }


# ========================
# GLOBAL SINGLETON
# ========================


def get_facade(provider: Optional[AttackProvider] = None) -> RTKFacade:
    return RTKFacade(provider=provider)


facade = get_facade()
