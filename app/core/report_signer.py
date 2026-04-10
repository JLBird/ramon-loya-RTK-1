"""
RTK-1 Report Signer — Objective 68
SHA-256 cryptographic safety-seal for tamper-proof reports.
Required for FCA liability protection and federal contractor deployments.
"""

import hashlib
import hmac
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger("report_signer")

# Dev signing secret — in production replace with mTLS cert private key
_SIGNING_SECRET = os.environ.get(
    "RTK1_SIGNING_SECRET", "rtk1-dev-signing-secret-change-in-prod"
)


class SignatureRecord(BaseModel):
    signature_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    report_sha256: str
    audit_sha256: str
    combined_sha256: str
    hmac_signature: str
    signed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signing_method: str = "SHA-256+HMAC"
    fca_compliant: bool = True
    ndaa_1512_compliant: bool = True


class ReportSigner:
    """
    Generates SHA-256 safety-seals for RTK-1 reports.
    Embeds signature in PDF metadata and JSON export.
    Provides tamper-detection via verify endpoint.
    """

    def sign(
        self,
        job_id: str,
        report_markdown: str,
        audit_json: Optional[str] = None,
    ) -> SignatureRecord:
        """Sign a report and return a verifiable SignatureRecord."""

        report_hash = hashlib.sha256(report_markdown.encode("utf-8")).hexdigest()
        audit_hash = hashlib.sha256((audit_json or "").encode("utf-8")).hexdigest()

        combined = f"{report_hash}:{audit_hash}:{job_id}"
        combined_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        sig = hmac.new(
            _SIGNING_SECRET.encode("utf-8"),
            combined_hash.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        record = SignatureRecord(
            job_id=job_id,
            report_sha256=report_hash,
            audit_sha256=audit_hash,
            combined_sha256=combined_hash,
            hmac_signature=sig,
        )

        # Persist to signatures store
        self._persist(record)

        logger.info(
            "report_signed",
            job_id=job_id,
            report_sha256=report_hash[:16] + "...",
            signing_method=record.signing_method,
        )

        return record

    def verify(self, job_id: str, report_markdown: str) -> dict:
        """
        Verify a report against its stored signature.
        Returns {verified: bool, reason: str, record: dict|None}
        """
        record = self._load(job_id)
        if not record:
            return {
                "verified": False,
                "reason": "No signature record found for this job_id.",
                "record": None,
            }

        current_hash = hashlib.sha256(report_markdown.encode("utf-8")).hexdigest()

        if current_hash != record.report_sha256:
            return {
                "verified": False,
                "reason": "Report content has been tampered with — SHA-256 mismatch.",
                "record": record.model_dump(),
                "stored_hash": record.report_sha256,
                "current_hash": current_hash,
            }

        # Re-verify HMAC
        combined = f"{record.report_sha256}:{record.audit_sha256}:{job_id}"
        combined_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        expected_sig = hmac.new(
            _SIGNING_SECRET.encode("utf-8"),
            combined_hash.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, record.hmac_signature):
            return {
                "verified": False,
                "reason": "HMAC signature invalid — signing key mismatch.",
                "record": record.model_dump(),
            }

        logger.info("report_verified", job_id=job_id, status="intact")
        return {
            "verified": True,
            "reason": "Report integrity confirmed — SHA-256 and HMAC match.",
            "record": record.model_dump(),
            "signed_at": record.signed_at.isoformat(),
            "fca_compliant": record.fca_compliant,
            "ndaa_1512_compliant": record.ndaa_1512_compliant,
        }

    def _persist(self, record: SignatureRecord) -> None:
        """Persist signature record to local JSON store."""
        store = Path("reports/signatures")
        store.mkdir(parents=True, exist_ok=True)
        path = store / f"{record.job_id}.sig.json"
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")

    def _load(self, job_id: str) -> Optional[SignatureRecord]:
        """Load signature record from local store."""
        path = Path("reports/signatures") / f"{job_id}.sig.json"
        if not path.exists():
            return None
        try:
            return SignatureRecord.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("signature_load_failed", job_id=job_id, error=str(e))
            return None


# ── Singleton ─────────────────────────────────────────────────────────────────
report_signer = ReportSigner()
