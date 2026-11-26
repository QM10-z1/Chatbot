import pytest
from app import store
from app.core.config import get_settings

def test_db_persistence(tmp_path, monkeypatch):
    """测试重新打开数据库连接后，旧会话和消息仍能读取"""
    db_file = tmp_path / "test_chat.db"
    monkeypatch.setenv("CHATBOT_DB_URL", f"sqlite:///{db_file}")
    get_settings.cache_clear()

    # 重新初始化引擎，确保使用了刚刚设置的临时数据库
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    store.engine = test_engine
    store.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    store.init_db()

    # 【关键】使用新的 append_chat_turn 写入一轮完整对话
    store.append_chat_turn("u1", "hello", "hi")
    store.append_chat_turn("u2", "你好", "你好呀")

    # 模拟“重启”：关闭当前连接（ORM 引擎会自动管理），重新初始化
    store.init_db()

    # 重新读取
    messages_u1 = store.get_messages("u1")
    messages_u2 = store.get_messages("u2")

    # 验证旧数据仍然存在，且不同会话互不混用
    assert messages_u1 is not None
    assert len(messages_u1) == 2
    assert messages_u1[0]["content"] == "hello"
    assert messages_u1[1]["content"] == "hi"

    assert messages_u2 is not None
    assert len(messages_u2) == 2
    assert messages_u2[0]["content"] == "你好"

    get_settings.cache_clear()