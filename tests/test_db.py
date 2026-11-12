import pytest
from app import store
from app.core.config import get_settings

def test_db_persistence(tmp_path, monkeypatch):
    db_file = tmp_path / "test_chat.db"
    monkeypatch.setenv("CHATBOT_DB_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()
    
    # 【关键】必须先创建会话，因为 messages 表有外键约束！
    store.get_or_create_session("u1")
    
    # 写入消息
    store.append_message("u1", "user", "hello")
    
    # 模拟重启后再次读取
    store.init_db()
    messages = store.get_messages("u1")
    assert messages is not None
    assert len(messages) == 1
    assert messages[0]["content"] == "hello"
    
    get_settings.cache_clear()