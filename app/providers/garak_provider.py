"""
Garak Attack Provider — NVIDIA's LLM vulnerability scanner.
Covers 100+ failure modes: hallucinations, data leakage, prompt injection,
toxicity, jailbreaks. CLI-based, plugin architecture, CI/CD friendly.
"""

import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

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

logger = get_logger("garak_provider")

# Garak probe classes mapped to OWASP LLM categories
GARAK_PROBE_MAP = {
    "prompt_injection": [
        "promptinject.HijackHateHumans",
        "promptinject.HijackKillHumans",
        "promptinject.HijackLongPrompt",
    ],
    "jailbreak": [
        "dan.Dan_11_0",
        "dan.DAN",
        "dan.DUDE",
        "dan.Ablation_Dan_11_0",
    ],
    "data_leakage": [
        "leakreplay.LiteratureComplete",
        "leakreplay.LiteratureCloze80",
    ],
    "hallucination": [
        "snowball.Primes",
        "snowball.Senators",
    ],
    "toxicity": [
        "realtoxicityprompts.RTPBlank",
    ],
}


class GarakProvider(AttackProvider):
    """
    Garak provider — wraps NVIDIA's garak CLI tool.
    Falls back to mock results if garak is not installed.
    Uses sys.executable to ensure venv Python is always used.
    """

    tool_name = "garak"

    def __init__(self, probe_categories: Optional[List[str]] = None):
        self._available = False
        self._probe_categories = probe_categories or ["prompt_injection", "jailbreak"]
        self._load()

    def _load(self) -> None:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "garak", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self._available = True
                logger.info("garak_loaded", version=result.stdout.strip())
            else:
                logger.warning("garak_not_available", stderr=result.stderr)
        except Exception as e:
            logger.warning("garak_load_failed", error=str(e))

    def is_available(self) -> bool:
        return self._available

    def _get_probes(self) -> List[str]:
        probes = []
        for category in self._probe_categories:
            probes.extend(GARAK_PROBE_MAP.get(category, []))
        return probes

    async def run_campaign(
        self,
        config: CampaignConfig,
        scorer_config: ScorerConfig,
    ) -> List[AttackResult]:

        if not self._available:
            logger.info("garak_mock_mode", target=config.target_model)
            return self._mock_results(config)

        probes = self._get_probes()
        results = []

        for i, probe in enumerate(probes[: config.num_sequences]):
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._run_single_probe,
                    config.target_model,
                    probe,
                    config.goal,
                    i,
                )
                results.append(result)
            except Exception as e:
                logger.error("garak_probe_failed", probe=probe, error=str(e))
                results.append(
                    AttackResult(
                        step=i,
                        turn_number=1,
                        escalation_depth=1,
                        tool_used=AttackTool.GARAK,
                        vector=AttackVector.SINGLE_TURN,
                        objective=config.goal,
                        prompt=probe,
                        response="",
                        outcome=AttackOutcome.ERROR,
                        success=False,
                        description=f"Garak probe {probe} errored: {str(e)}",
                    )
                )

        logger.info("garak_campaign_complete", total=len(results))
        return results

    def _run_single_probe(
        self,
        target_model: str,
        probe_class: str,
        goal: str,
        step: int,
    ) -> AttackResult:
        """Run a single Garak probe synchronously using venv Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.jsonl"

            cmd = [
                sys.executable,
                "-m",
                "garak",
                "--model_type",
                "openai",
                "--model_name",
                target_model,
                "--probes",
                probe_class,
                "--report_prefix",
                str(report_path),
                "--parallel_attempts",
                "1",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={
                    **__import__("os").environ,
                    "OPENAI_API_KEY": settings.anthropic_api_key,
                    "OPENAI_BASE_URL": settings.anthropic_openai_compat_endpoint,
                },
            )

            success = False
            response = result.stdout[:500] if result.stdout else ""

            if report_path.exists():
                try:
                    with open(report_path) as f:
                        for line in f:
                            data = json.loads(line)
                            if data.get("status") == "failed":
                                success = True
                                break
                except Exception:
                    pass

            outcome = AttackOutcome.SUCCESS if success else AttackOutcome.FAILURE

            return AttackResult(
                step=step,
                turn_number=1,
                escalation_depth=1,
                tool_used=AttackTool.GARAK,
                vector=AttackVector.SINGLE_TURN,
                objective=goal,
                prompt=probe_class,
                response=response,
                outcome=outcome,
                success=success,
                description=f"Garak probe: {probe_class} — {outcome.value}",
            )

    def _mock_results(self, config: CampaignConfig) -> List[AttackResult]:
        probes = self._get_probes()
        return [
            AttackResult(
                step=i,
                turn_number=1,
                escalation_depth=1,
                tool_used=AttackTool.MOCK,
                vector=AttackVector.SINGLE_TURN,
                objective=config.goal,
                prompt=probe,
                response=f"Mock Garak result for {probe}",
                outcome=AttackOutcome.UNDETERMINED,
                success=False,
                description=f"Mock Garak probe {probe} (garak not installed)",
            )
            for i, probe in enumerate(probes[: config.num_sequences])
        ]
