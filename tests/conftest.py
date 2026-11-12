import pytest
from fastapi.testclient import TestClient
from app import store
from app.main import app
import app.llm as llm

@pytest.fixture(autouse=True)
def clean_store(monkeypatch):
    from app.core.config import get_settings
    
    # 1. 强制设置环境变量为内存库
    monkeypatch.setenv("CHATBOT_DB_URL", "sqlite:///:memory:")
    
    # 2. 清理缓存，确保设置生效
    get_settings.cache_clear()
    
    # 3. 初始化数据库
    store.init_db()
    
    yield
    
    # 4. 测试结束后清空数据并清理缓存
    store.clear_all()
    get_settings.cache_clear()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    def fake_call_model(messages):
        last_user = next(m for m in reversed(messages) if m["role"] == "user")
        return f"echo:{last_user['content']}"
    def fake_call_model_stream(messages):
        last_user = next(m for m in reversed(messages) if m["role"] == "user")
        for ch in f"echo:{last_user['content']}":
            yield ch
    monkeypatch.setattr("app.routers.chat.call_model", fake_call_model)
    monkeypatch.setattr("app.routers.chat.call_model_stream", fake_call_model_stream)
    monkeypatch.setattr("app.routers.study.call_model", fake_call_model)