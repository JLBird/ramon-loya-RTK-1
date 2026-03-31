from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional
import os

# ── Strong debug for Windows / project-root issues ─────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(project_root, ".env")

print(f"🔍 DEBUG: Project root detected as → {project_root}")
print(f"🔍 DEBUG: Looking for .env at → {env_path}")
print(f"🔍 DEBUG: .env file exists? → {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        print("🔍 DEBUG: First few lines of .env:")
        print("".join(f.readlines()[:5]))

class Settings(BaseSettings):
    """Central configuration for RTK-1 (Claude-orchestrated red teaming)."""

    model_config = SettingsConfigDict(
        env_file=env_path,              # explicit absolute path
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required credentials
    anthropic_api_key: str

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
        return self


# Global singleton used throughout the app
settings = Settings()