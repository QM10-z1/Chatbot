import sys
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, ValidationError

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CHATBOT_", extra="ignore")

    api_key: SecretStr = Field(...)
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = Field(0.7, ge=0, le=2)

@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError:
        # 校验错误原样抛出，供测试捕获
        raise
    except Exception as e:
        # 其他未知错误才打印并退出
        print(f"配置错误: {e}", file=sys.stderr)
        raise SystemExit(1)
