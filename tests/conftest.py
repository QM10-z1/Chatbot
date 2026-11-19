import pytest
from fastapi.testclient import TestClient
from app import store
from app.main import app
import app.llm as llm
from app.core.config import get_settings

@pytest.fixture(autouse=True)
def clean_store(monkeypatch, tmp_path):
    # 使用 pytest 提供的临时路径生成临时数据库
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("CHATBOT_DB_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    
    # 重新初始化引擎和建表
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base
    
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    
    # 修改 store 里的引擎和 SessionLocal 指向测试库
    store.engine = test_engine
    store.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    yield
    
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