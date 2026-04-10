"""
promptfoo Attack Provider — regression testing and CI/CD gate.
Best-in-class for systematic LLM evaluation and pipeline integration.
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List

import yaml

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.models import (
    AttackOutcome,
    AttackResult,
    AttackTool,
    AttackVector,
    CampaignConfig,
    ScorerConfig,
)
from app.providers.base import AttackProvider

logger = get_logger("promptfoo_provider")

# Standard promptfoo red team plugins mapped to OWASP categories
PROMPTFOO_PLUGINS = [
    "prompt-injection",
    "jailbreak",
    "harmful:hate",
    "harmful:privacy",
    "pii:direct",
    "rbac",
    "system-prompt-exfiltration",
]


class PromptfooProvider(AttackProvider):
    """
    promptfoo provider — wraps promptfoo CLI for systematic LLM evaluation.
    Generates YAML config, runs evaluation, parses results into domain models.
    Falls back to mock if promptfoo not installed.
    """

    tool_name = "promptfoo"

    def __init__(self, llm=None):
        self._available = False
        self._load()

    def _load(self) -> None:
        try:
            result = subprocess.run(
                [r"C:\Users\joshl\AppData\Roaming\npm\promptfoo.cmd", "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                self._available = True
                logger.info("promptfoo_loaded", version=result.stdout.strip())
            else:
                logger.warning("promptfoo_not_available")
        except Exception as e:
            logger.warning("promptfoo_load_failed", error=str(e))

    def is_available(self) -> bool:
        return self._available

    def _build_config(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
        output_path: str,
    ) -> dict:
        """Build promptfoo YAML evaluation config."""
        return {
            "description": f"RTK-1 Red Team: {config.goal}",
            "targets": [
                {
                    "id": "openai:chat:" + config.target_model,
                    "config": {
                        "apiBaseUrl": settings.anthropic_openai_compat_endpoint,
                        "apiKey": settings.anthropic_api_key,
                    },
                }
            ],
            "redteam": {
                "purpose": config.goal,
                "numTests": config.num_sequences,
                "plugins": PROMPTFOO_PLUGINS[: config.num_sequences],
                "strategies": ["jailbreak", "prompt-injection"],
            },
            "outputPath": output_path,
        }

    async def run_campaign(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:

        if not self._available:
            logger.info("promptfoo_mock_mode")
            return self._mock_results(config)

        try:
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_sync,
                config,
                scorer_config,
            )
            return results
        except Exception as e:
            logger.error("promptfoo_campaign_failed", error=str(e))
            logger.info("promptfoo_falling_back_to_mock")
            return self._mock_results(config)

    def _run_sync(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "promptfooconfig.yaml"
            output_path = Path(tmpdir) / "results.json"

            pf_config = self._build_config(config, scorer_config, str(output_path))

            with open(config_path, "w") as f:
                yaml.dump(pf_config, f)

            result = subprocess.run(
                [
                    r"C:\Users\joshl\AppData\Roaming\npm\promptfoo.cmd",
                    "redteam",
                    "run",
                    "--config",
                    str(config_path),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if not output_path.exists():
                logger.warning("promptfoo_no_output", stderr=result.stderr[:200])
                return self._mock_results(config)

            with open(output_path) as f:
                data = json.load(f)

            return self._parse_results(data, config)

    def _parse_results(
        self,
        data: dict,
        config: CampaignConfig,
    ) -> List[AttackResult]:
        results = []
        evals = data.get("results", {}).get("results", [])

        for i, eval_result in enumerate(evals):
            success = not eval_result.get("pass", True)
            prompt = eval_result.get("prompt", {}).get("raw", config.goal)
            response = eval_result.get("response", {}).get("output", "")
            plugin = eval_result.get("metadata", {}).get("pluginId", "unknown")

            results.append(
                AttackResult(
                    step=i,
                    turn_number=1,
                    escalation_depth=1,
                    tool_used=AttackTool.PROMPTFOO,
                    vector=AttackVector.SINGLE_TURN,
                    objective=config.goal,
                    prompt=prompt[:500],
                    response=response[:500],
                    outcome=AttackOutcome.SUCCESS if success else AttackOutcome.FAILURE,
                    success=success,
                    description=f"promptfoo plugin: {plugin} — {'FAIL' if success else 'PASS'}",
                )
            )

        logger.info("promptfoo_results_parsed", total=len(results))
        return results

    def _mock_results(self, config: CampaignConfig) -> List[AttackResult]:
        return [
            AttackResult(
                step=i,
                turn_number=1,
                escalation_depth=1,
                tool_used=AttackTool.MOCK,
                vector=AttackVector.SINGLE_TURN,
                objective=config.goal,
                prompt=PROMPTFOO_PLUGINS[i % len(PROMPTFOO_PLUGINS)],
                response="Mock promptfoo result (promptfoo not installed)",
                outcome=AttackOutcome.UNDETERMINED,
                success=False,
                description=f"Mock promptfoo probe {i} (install: npm i -g promptfoo)",
            )
            for i in range(config.num_sequences)
        ]
