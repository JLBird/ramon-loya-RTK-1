from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv
import os

# Force load .env (absolute path for Windows reliability)
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path, override=True)

print(f"🔍 DEBUG: .env path = {env_path}")
print(f"🔍 DEBUG: Raw ANTHROPIC_API_KEY = {'YES' if os.getenv('ANTHROPIC_API_KEY', '').startswith('sk-ant-') else 'NOT_FOUND'}")

class Settings(BaseSettings):
    anthropic_api_key: Optional[str] = None   # Optional so server starts

    ollama_host: str = "http://localhost:11434"
    rate_limit_per_minute: int = 60
    log_level: str = "INFO"

    openai_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

if settings.anthropic_api_key and settings.anthropic_api_key.startswith("sk-ant-"):
    print("✅ ANTHROPIC_API_KEY loaded successfully!")
else:
    print("❌ Key missing - check .env file")