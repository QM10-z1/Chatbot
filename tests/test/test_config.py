import pytest
from pydantic import ValidationError
from config import get_settings

@pytest.fixture(autouse=True)
def clear_cache():
    """每个测试前后自动清理 lru_cache 缓存"""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

def test_default_values(monkeypatch):
    # 强制设置所有环境变量，覆盖 .env 文件的干扰
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    monkeypatch.setenv("CHATBOT_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("CHATBOT_MODEL", "deepseek-chat")
    monkeypatch.setenv("CHATBOT_TEMPERATURE", "0.7")

    settings = get_settings()

    assert settings.base_url == "https://api.deepseek.com"
    assert settings.model == "deepseek-chat"
    assert settings.temperature == 0.7

def test_temperature_validation(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    # 设置非法温度值
    monkeypatch.setenv("CHATBOT_TEMPERATURE", "5")

    # 期望抛出 Pydantic 的校验错误，而不是 SystemExit
    with pytest.raises(ValidationError):
        get_settings()

def test_secret_str_not_printed(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    settings = get_settings()

    assert settings.api_key.get_secret_value() == "sk-test"
    assert "sk-test" not in str(settings)
