"""
PyRIT attack provider — implements AttackProvider using CrescendoAttack.
All PyRIT internals are contained here. Nothing above this file sees PyRIT objects.
"""

import traceback
from typing import List

import tenacity
from langchain_anthropic import ChatAnthropic
from tenacity import stop_after_attempt, wait_exponential

from app.core.config import settings
from app.domain.models import (
    AttackOutcome,
    AttackResult,
    AttackTool,
    AttackVector,
    CampaignConfig,
    ScorerConfig,
)
from app.providers.base import AttackProvider
from app.pyrit_langchain_target import LangChainAnthropicTarget


class PyRITProvider(AttackProvider):
    """
    Concrete attack provider using Microsoft PyRIT 0.12.0.
    Uses CrescendoAttack + SelfAskTrueFalseScorer with LangChain bridge.
    """

    tool_name = "pyrit"

    def __init__(self, llm: ChatAnthropic):
        self._llm = llm
        self._available = False
        self._load()

    def _load(self):
        try:
            from pyrit.executor.attack.core.attack_config import (
                AttackAdversarialConfig,
                AttackScoringConfig,
            )
            from pyrit.executor.attack.multi_turn.crescendo import (
                AttackOutcome as PyRITOutcome,
            )
            from pyrit.executor.attack.multi_turn.crescendo import (
                CrescendoAttack,
            )
            from pyrit.memory import CentralMemory, SQLiteMemory
            from pyrit.prompt_target import OpenAIChatTarget
            from pyrit.score.true_false.self_ask_true_false_scorer import (
                SelfAskTrueFalseScorer,
                TrueFalseQuestion,
            )

            CentralMemory.set_memory_instance(SQLiteMemory())

            self._CrescendoAttack = CrescendoAttack
            self._PyRITOutcome = PyRITOutcome
            self._AttackAdversarialConfig = AttackAdversarialConfig
            self._AttackScoringConfig = AttackScoringConfig
            self._SelfAskTrueFalseScorer = SelfAskTrueFalseScorer
            self._TrueFalseQuestion = TrueFalseQuestion
            self._OpenAIChatTarget = OpenAIChatTarget

            self._adversarial_target = LangChainAnthropicTarget(llm=self._llm)
            self._judge_target = LangChainAnthropicTarget(llm=self._llm)

            self._available = True
            print(
                "✅ PyRITProvider loaded — CrescendoAttack + SelfAskTrueFalseScorer active"
            )

        except Exception:
            print("❌ PyRITProvider failed to load:")
            print(traceback.format_exc())

    def is_available(self) -> bool:
        return self._available

    @tenacity.retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _execute_sequence(
        self,
        attack,
        goal: str,
        sequence_index: int,
    ) -> AttackResult:
        """Single sequence execution with tenacity retry."""
        result = await attack.execute_async(objective=goal)
        success = result.outcome == self._PyRITOutcome.SUCCESS

        outcome_map = {
            "success": AttackOutcome.SUCCESS,
            "failure": AttackOutcome.FAILURE,
            "undetermined": AttackOutcome.UNDETERMINED,
        }
        domain_outcome = outcome_map.get(
            result.outcome.value, AttackOutcome.UNDETERMINED
        )

        return AttackResult(
            step=sequence_index,
            turn_number=result.executed_turns,
            escalation_depth=result.executed_turns,
            tool_used=AttackTool.PYRIT,
            vector=AttackVector.CRESCENDO,
            objective=goal,
            prompt=goal,
            response=str(result.last_response) if result.last_response else "",
            outcome=domain_outcome,
            success=success,
            description=f"Crescendo sequence {sequence_index} — {result.outcome.value}",
        )

    async def run_campaign(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:

        if not self._available:
            print(f"🔄 [Mock PyRIT] Would have run {config.num_sequences} sequences")
            return [
                AttackResult(
                    step=i,
                    turn_number=config.turns_per_sequence,
                    escalation_depth=config.turns_per_sequence,
                    tool_used=AttackTool.MOCK,
                    vector=AttackVector.CRESCENDO,
                    objective=config.goal,
                    prompt=config.goal,
                    response="Mock response (PyRIT not installed)",
                    outcome=AttackOutcome.UNDETERMINED,
                    success=False,
                    description=f"Mock Crescendo sequence {i}",
                )
                for i in range(config.num_sequences)
            ]

        # Normalize target model
        target_model = config.target_model
        if (
            not target_model
            or "ollama" in target_model.lower()
            or "llama" in target_model.lower()
        ):
            print(f"⚠️  Normalizing target_model '{target_model}' → claude-sonnet-4-6")
            target_model = "claude-sonnet-4-6"

        print(
            f"🚀 PyRITProvider: {config.num_sequences} sequences × {config.turns_per_sequence} turns → {target_model}"
        )

        attack_target = self._OpenAIChatTarget(
            model_name=target_model,
            endpoint=settings.anthropic_openai_compat_endpoint,
            api_key=settings.anthropic_api_key,
        )

        adversarial_config = self._AttackAdversarialConfig(
            target=self._adversarial_target,
        )

        # Use customer-defined scorer config
        objective_scorer = self._SelfAskTrueFalseScorer(
            chat_target=self._judge_target,
            true_false_question=self._TrueFalseQuestion(
                true_description=scorer_config.true_description,
                false_description=scorer_config.false_description,
            ),
        )

        scoring_config = self._AttackScoringConfig(
            objective_scorer=objective_scorer,
            use_score_as_feedback=True,
        )

        results: List[AttackResult] = []
        for i in range(config.num_sequences):
            print(f"   → Sequence {i + 1}/{config.num_sequences} ...")
            try:
                attack = self._CrescendoAttack(
                    objective_target=attack_target,
                    attack_adversarial_config=adversarial_config,
                    attack_scoring_config=scoring_config,
                    max_turns=config.turns_per_sequence,
                )
                result = await self._execute_sequence(attack, config.goal, i)
                print(f"      ✓ Sequence {i + 1} — outcome: {result.outcome.value}")
                results.append(result)

            except Exception as e:
                print(f"      ❌ Sequence {i + 1} failed: {e}")
                print(traceback.format_exc())
                results.append(
                    AttackResult(
                        step=i,
                        turn_number=0,
                        escalation_depth=0,
                        tool_used=AttackTool.PYRIT,
                        vector=AttackVector.CRESCENDO,
                        objective=config.goal,
                        prompt=config.goal,
                        response="",
                        outcome=AttackOutcome.ERROR,
                        success=False,
                        description=f"Sequence {i} errored: {str(e)}",
                    )
                )

        print(f"🏁 PyRITProvider: {len(results)} sequences completed")
        return results
