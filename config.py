import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CHATBOT_", extra="ignore")

    api_key: SecretStr = Field(...)
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = Field(0.7, ge=0, le=2)

def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        print(f"配置错误: {e}", file=sys.stderr)
        raise SystemExit(1)

settings = get_settings()
