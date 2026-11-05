"""内存会话存储。读写集中在此模块，方便以后换成数据库。"""

from typing import Optional

# session_id -> [{"role": "user"/"assistant", "content": "..."}]
_sessions: dict[str, list[dict]] = {}


def get_or_create_session(session_id: str) -> list[dict]:
    """获取会话消息列表，不存在则创建空会话。"""
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


def append_message(session_id: str, role: str, content: str) -> None:
    """向会话追加一条消息。"""
    get_or_create_session(session_id).append({"role": role, "content": content})


def list_sessions() -> list[str]:
    """返回所有会话 ID。"""
    return list(_sessions.keys())


def session_exists(session_id: str) -> bool:
    return session_id in _sessions


def get_messages(session_id: str) -> Optional[list[dict]]:
    """返回会话消息记录，不存在返回 None。"""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """删除会话，返回是否删除成功。"""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def clear_all() -> None:
    """清空所有会话（测试用）。"""
    _sessions.clear()