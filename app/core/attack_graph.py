"""
RTK-1 Attack Graph — builds a visual map of which attack paths
succeeded, failed, and how Crescendo escalation trees branched.
Pure data structure — no LLM calls required.
"""

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("attack_graph")


class AttackGraphBuilder:
    """
    Builds attack graph data from campaign results.
    Output is consumed by the Streamlit portal and PDF reports.
    """

    def build_graph(self, results: list) -> Dict[str, Any]:
        """
        Build a directed graph from attack results.
        Nodes = turns, Edges = escalation paths, Color = success/failure.
        """
        if not results:
            return {"nodes": [], "edges": [], "summary": {}}

        nodes = []
        edges = []

        # Root node
        nodes.append({
            "id": "root",
            "label": "Campaign Start",
            "type": "root",
            "color": "#4A90D9",
            "size": 20,
        })

        successful = 0
        failed = 0

        for seq_idx, result in enumerate(results):
            seq_id = f"seq_{seq_idx}"
            success = getattr(result, "success", False)
            turns = getattr(result, "turn_number", 1)
            escalation = getattr(result, "escalation_depth", 1)
            description = getattr(result, "description", f"Sequence {seq_idx + 1}")

            if success:
                successful += 1
                color = "#E74C3C"
                label = f"SEQ {seq_idx + 1}\n✅ SUCCESS"
            else:
                failed += 1
                color = "#2ECC71"
                label = f"SEQ {seq_idx + 1}\n❌ BLOCKED"

            nodes.append({
                "id": seq_id,
                "label": label,
                "type": "sequence",
                "color": color,
                "size": 12 + escalation * 2,
                "turns": turns,
                "escalation_depth": escalation,
                "description": description[:100],
                "success": success,
            })

            edges.append({
                "from": "root",
                "to": seq_id,
                "label": f"Turn {turns}",
                "color": color,
            })

            # Add turn-level nodes for high-escalation sequences
            if escalation >= 4:
                for turn_idx in range(min(turns, escalation)):
                    turn_node_id = f"{seq_id}_turn_{turn_idx}"
                    is_final = turn_idx == turns - 1
                    nodes.append({
                        "id": turn_node_id,
                        "label": f"T{turn_idx + 1}",
                        "type": "turn",
                        "color": "#E74C3C" if (is_final and success) else "#95A5A6",
                        "size": 8,
                    })
                    prev = seq_id if turn_idx == 0 else f"{seq_id}_turn_{turn_idx - 1}"
                    edges.append({
                        "from": prev,
                        "to": turn_node_id,
                        "label": "",
                        "color": "#95A5A6",
                    })

        total = len(results)
        asr = round((successful / total) * 100, 2) if total > 0 else 0.0

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total_sequences": total,
                "successful": successful,
                "failed": failed,
                "asr": asr,
                "graph_type": "crescendo_escalation_tree",
            },
        }

    def to_mermaid(self, results: list) -> str:
        """
        Generate Mermaid diagram markup from attack results.
        Renderable directly in GitHub markdown and PDF reports.
        """
        if not results:
            return "graph TD\n    A[No results]"

        lines = ["graph TD"]
        lines.append("    ROOT([Campaign Start]) --> SPLIT{Attack Sequences}")

        for idx, result in enumerate(results):
            success = getattr(result, "success", False)
            turns = getattr(result, "turn_number", 1)
            node_id = f"SEQ{idx + 1}"
            icon = "✅" if success else "❌"
            status = "SUCCESS" if success else "BLOCKED"

            if success:
                lines.append(
                    f'    SPLIT --> {node_id}["Seq {idx + 1} | {turns} turns\\n{icon} {status}"]'
                )
                lines.append(f"    style {node_id} fill:#E74C3C,color:#fff")
            else:
                lines.append(
                    f'    SPLIT --> {node_id}["Seq {idx + 1} | {turns} turns\\n{icon} {status}"]'
                )
                lines.append(f"    style {node_id} fill:#2ECC71,color:#fff")

        total = len(results)
        successful = sum(1 for r in results if getattr(r, "success", False))
        asr = round((successful / total) * 100, 2) if total > 0 else 0.0
        lines.append(f'    SPLIT --> RESULT(["ASR: {asr}%"])')

        return "\n".join(lines)

    def save_graph(self, job_id: str, graph_data: Dict) -> None:
        """Save graph data to campaign DB for later retrieval."""
        with sqlite3.connect(settings.campaign_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attack_graphs (
                    job_id TEXT PRIMARY KEY,
                    graph_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute(
                """
                INSERT OR REPLACE INTO attack_graphs (job_id, graph_json, created_at)
                VALUES (?, ?, ?)
                """,
                (job_id, json.dumps(graph_data), datetime.now(UTC).isoformat()),
            )
            conn.commit()
        logger.info("attack_graph_saved", job_id=job_id)

    def load_graph(self, job_id: str) -> Optional[Dict]:
        """Load graph data for a specific campaign."""
        with sqlite3.connect(settings.campaign_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attack_graphs (
                    job_id TEXT PRIMARY KEY,
                    graph_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            row = conn.execute(
                "SELECT graph_json FROM attack_graphs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])


attack_graph_builder = AttackGraphBuilder()
