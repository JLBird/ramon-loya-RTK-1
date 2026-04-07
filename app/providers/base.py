"""
Abstract attack provider interface — swap PyRIT, Garak, or promptfoo
without touching the orchestrator.
"""

from abc import ABC, abstractmethod
from typing import List

from app.domain.models import AttackResult, CampaignConfig, ScorerConfig


class AttackProvider(ABC):
    """
    Base class for all attack providers.
    Concrete implementations: PyRITProvider, GarakProvider, PromptfooProvider
    """

    @abstractmethod
    async def run_campaign(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:
        """
        Execute a full attack campaign and return clean AttackResult domain objects.
        Never return raw provider objects above this layer.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider's dependencies are installed and ready."""
        ...

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Human-readable provider name for logging."""
        ...
