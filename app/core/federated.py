"""
RTK-1 Federated Red Teaming Coordinator — Objective 66.
Coordinates multiple RTK-1 instances attacking from different
geographic locations and IP ranges.
Tests rate limiting, geo-blocking, and anomaly detection systems.
"""

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Dict, List, Optional

import httpx

from app.core.logging import get_logger
from app.domain.models import CampaignConfig

logger = get_logger("federated")


class FederatedCoordinator:
    """
    Coordinates RTK-1 instances for distributed attack campaigns.
    Each node attacks from a different source, testing whether
    target defenses block single-source patterns.

    In production: each node_url is a separate RTK-1 deployment.
    In development: uses localhost with different ports or mock results.
    """

    def __init__(self, node_urls: Optional[List[str]] = None):
        self._nodes = node_urls or []
        self._local_url = "http://localhost:8000"

    def register_node(self, url: str) -> None:
        if url not in self._nodes:
            self._nodes.append(url)
            logger.info(
                "federated_node_registered", url=url, total_nodes=len(self._nodes)
            )

    async def run_federated_campaign(
        self,
        config: CampaignConfig,
        use_local_fallback: bool = True,
    ) -> Dict:
        """
        Run coordinated campaign across all registered nodes.
        Each node runs the same campaign independently.
        Results are aggregated into a unified report.
        """
        campaign_id = str(uuid.uuid4())
        logger.info(
            "federated_campaign_started",
            campaign_id=campaign_id,
            nodes=len(self._nodes),
        )

        if not self._nodes and use_local_fallback:
            logger.info("federated_no_nodes_using_local")
            return await self._run_local_only(config, campaign_id)

        node_tasks = [
            self._run_on_node(node_url, config, campaign_id) for node_url in self._nodes
        ]

        node_results = await asyncio.gather(*node_tasks, return_exceptions=True)

        valid_results = [r for r in node_results if isinstance(r, dict)]
        failed_nodes = [r for r in node_results if isinstance(r, Exception)]

        if not valid_results and use_local_fallback:
            logger.warning("all_nodes_failed_using_local")
            local = await self._run_local_only(config, campaign_id)
            valid_results = [local]

        return self._aggregate_results(valid_results, failed_nodes, campaign_id, config)

    async def _run_on_node(
        self,
        node_url: str,
        config: CampaignConfig,
        campaign_id: str,
    ) -> Dict:
        """Run campaign on a single remote RTK-1 node."""
        try:
            async with httpx.AsyncClient(timeout=1800) as client:
                response = await client.post(
                    f"{node_url}/api/v1/redteam/crescendo",
                    json={
                        "target_model": config.target_model,
                        "goal": config.goal,
                        "attack_type": "crescendo",
                        "customer_success_metrics": config.customer_success_metrics,
                    },
                )
                result = response.json()
                result["node_url"] = node_url
                result["campaign_id"] = campaign_id
                logger.info(
                    "node_campaign_complete", node=node_url, asr=result.get("asr")
                )
                return result

        except Exception as e:
            logger.error("node_campaign_failed", node=node_url, error=str(e))
            raise

    async def _run_local_only(self, config: CampaignConfig, campaign_id: str) -> Dict:
        """Run on local RTK-1 instance when no remote nodes configured."""
        try:
            async with httpx.AsyncClient(timeout=1800) as client:
                response = await client.post(
                    f"{self._local_url}/api/v1/redteam/crescendo",
                    json={
                        "target_model": config.target_model,
                        "goal": config.goal,
                        "attack_type": "crescendo",
                        "customer_success_metrics": config.customer_success_metrics,
                    },
                )
                result = response.json()
                result["node_url"] = "localhost"
                result["campaign_id"] = campaign_id
                return result
        except Exception as e:
            logger.error("local_federated_failed", error=str(e))
            return {
                "node_url": "localhost",
                "campaign_id": campaign_id,
                "asr": 0.0,
                "sequences_run": 0,
                "status": "error",
                "error": str(e),
            }

    def _aggregate_results(
        self,
        results: List[Dict],
        failed_nodes: List[Exception],
        campaign_id: str,
        config: CampaignConfig,
    ) -> Dict:
        """Aggregate results from all nodes into unified report."""
        if not results:
            return {
                "campaign_id": campaign_id,
                "status": "failed",
                "nodes_attempted": len(self._nodes),
                "nodes_succeeded": 0,
                "combined_asr": 0.0,
            }

        total_sequences = sum(r.get("sequences_run", 0) for r in results)
        asrs = [r.get("asr", 0.0) for r in results if r.get("status") == "completed"]
        combined_asr = round(sum(asrs) / len(asrs), 2) if asrs else 0.0
        max_asr = max(asrs) if asrs else 0.0
        min_asr = min(asrs) if asrs else 0.0

        logger.info(
            "federated_campaign_complete",
            campaign_id=campaign_id,
            nodes_succeeded=len(results),
            combined_asr=combined_asr,
        )

        return {
            "campaign_id": campaign_id,
            "target_model": config.target_model,
            "goal": config.goal,
            "status": "completed",
            "nodes_attempted": len(self._nodes) or 1,
            "nodes_succeeded": len(results),
            "nodes_failed": len(failed_nodes),
            "total_sequences": total_sequences,
            "combined_asr": combined_asr,
            "max_asr_across_nodes": max_asr,
            "min_asr_across_nodes": min_asr,
            "asr_variance": round(max_asr - min_asr, 2),
            "per_node_results": [
                {
                    "node": r.get("node_url", "unknown"),
                    "asr": r.get("asr", 0.0),
                    "sequences": r.get("sequences_run", 0),
                    "status": r.get("status", "unknown"),
                }
                for r in results
            ],
            "interpretation": (
                f"Across {len(results)} attack nodes, combined ASR was {combined_asr}%. "
                f"ASR variance of {round(max_asr - min_asr, 2)}% suggests "
                f"{'consistent vulnerability regardless of source' if max_asr - min_asr < 20 else 'source-dependent defenses — rate limiting or geo-blocking may be active'}."
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }


# Global singleton — register remote nodes via register_node()
coordinator = FederatedCoordinator()
