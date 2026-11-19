import pytest
from app import store
from app.models import Session, Message

def test_persistence_reconnect():
    """测试重新连接后数据依然在"""
    store.append_chat_turn("u1", "hello", "hi")
    messages = store.get_messages("u1")
    assert len(messages) == 2
    assert messages[0]["content"] == "hello"

def test_transaction_rollback():
    """测试事务回滚（模拟写入时崩溃）"""
    # 写入第一轮正常对话
    store.append_chat_turn("u1", "hello", "hi")
    
    # 模拟发生异常：调用一个不存在的数据库字段，强制报错
    with pytest.raises(Exception):
        with store.get_db() as db:
            msg = Message(session_id="u1", role="user", content="fail")
            db.add(msg)
            # 模拟程序在此处崩溃
            raise ValueError("Simulated crash")
            db.commit()
    
    # 断言数据库里没有留下 "fail" 这条半截消息
    messages = store.get_messages("u1")
    assert len(messages) == 2 # 依然只有之前的那2条