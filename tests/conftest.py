import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app
import app.llm as llm


@pytest.fixture(autouse=True)
def clean_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    def fake_call_model(messages):
        # 回显最后一条 user 消息，便于断言
        last_user = next(m for m in reversed(messages) if m["role"] == "user")
        return f"echo:{last_user['content']}"

    def fake_call_model_stream(messages):
        last_user = next(m for m in reversed(messages) if m["role"] == "user")
        for ch in f"echo:{last_user['content']}":
            yield ch

    
    monkeypatch.setattr("app.routers.chat.call_model", fake_call_model)
    monkeypatch.setattr("app.routers.chat.call_model_stream", fake_call_model_stream)
    monkeypatch.setattr("app.routers.study.call_model", fake_call_model)