import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# 动态计算项目根目录，确保无论在哪运行都能找到 .env
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # 修改点：使用绝对路径
        env_prefix="CHATBOT_", 
        extra="ignore"
    )

    api_key: SecretStr = Field(...)
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = Field(0.7, ge=0, le=2)

    db_url: str = Field("sqlite:///./chat.db", description="数据库连接字符串")

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