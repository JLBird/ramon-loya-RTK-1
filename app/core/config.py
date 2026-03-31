from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional
import os

# Absolute .env path for reliable loading on Windows
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")


class Settings(BaseSettings):
    """Central configuration for RTK-1 (Claude-orchestrated red teaming)."""

    model_config = SettingsConfigDict(
        env_file=env_path,  # explicit absolute path
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any extra env vars
    )

    # Required credentials
    anthropic_api_key: str  # Will fail fast if missing from .env

    # Optional / defaulted settings
    ollama_host: str = "http://localhost:11434"
    rate_limit_per_minute: int = 60
    log_level: str = "INFO"
    openai_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None

    @model_validator(mode="after")
    def validate_anthropic_key(self):
        """Friendly startup feedback for the main LLM key."""
        if self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant-"):
            print("✅ ANTHROPIC_API_KEY loaded successfully!")
        else:
            print("❌ ANTHROPIC_API_KEY missing or invalid - check .env file")
            # raise ValueError("Missing Anthropic API key")  # uncomment for hard failure
        return self


# Global singleton used throughout the app
settings = Settings()
