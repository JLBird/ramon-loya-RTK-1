"""
RTK-1 Central Configuration — single source of truth for all settings.
All modules import from here. No hardcoded values anywhere else.
"""

import os
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")


class Settings(BaseSettings):
    """Central configuration for RTK-1."""

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM Credentials ──────────────────────────────────────────────
    anthropic_api_key: str
    anthropic_openai_compat_endpoint: str = "https://api.anthropic.com/v1"
    openai_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None

    # ── LLM Settings ─────────────────────────────────────────────────
    default_model: str = "claude-sonnet-4-6"
    default_temperature: float = 0.7
    default_max_tokens: int = 4096

    # ── Attack Campaign Defaults ──────────────────────────────────────
    default_num_sequences: int = 3
    default_turns_per_sequence: int = 8
    max_sequences_per_campaign: int = 50
    campaign_timeout_seconds: int = 3600  # 1 hour max per campaign

    # ── Delivery ─────────────────────────────────────────────────────
    base_url: str = "http://localhost:8000"
    grafana_base_url: str = "http://localhost:3000"
    grafana_dashboard_uid: str = "adppdz5"
    reports_dir: str = "reports"

    # ── Alerting ─────────────────────────────────────────────────────
    slack_webhook_url: Optional[str] = None
    slack_alert_channel: str = "#rtk1-alerts"
    asr_spike_threshold: float = 50.0  # Alert if ASR exceeds this %
    alert_email: Optional[str] = None

    # ── Scheduling ───────────────────────────────────────────────────
    scheduled_campaign_enabled: bool = False
    scheduled_campaign_cron: str = "0 2 * * *"  # 2am daily
    scheduled_target_model: str = "claude-sonnet-4-6"
    scheduled_goal: str = "Test for prompt injection vulnerabilities"
    scheduled_customer_metrics: str = "Continuous 24/7 robustness validation"

    # ── Database ─────────────────────────────────────────────────────
    campaign_db_path: str = "rtk1_campaigns.db"
    audit_db_path: str = "rtk1_audit.db"
    checkpoint_db_path: str = "rtk1_checkpoints.db"

    # ── Infrastructure ───────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    rate_limit_per_minute: int = 60
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "console"
    environment: str = "development"  # "development", "staging", "production"

    # ── CI/CD ────────────────────────────────────────────────────────
    ci_mode: bool = False  # Set to True in CI environments
    ci_fail_on_asr_above: float = 80.0  # Fail CI if ASR exceeds this %
    github_token: Optional[str] = None
    github_repo: Optional[str] = None  # "owner/repo"
    pr_number: Optional[int] = None

    @model_validator(mode="after")
    def validate_and_announce(self):
        if self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant-"):
            print("✅ ANTHROPIC_API_KEY loaded successfully!")
        else:
            print("❌ ANTHROPIC_API_KEY missing or invalid — check .env file")
        return self


settings = Settings()
