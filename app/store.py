import sqlite3
from app.core.config import get_settings

# 全局连接缓存（专门用来对付 :memory: 测试）
_global_conn = None

def _get_conn():
    global _global_conn
    db_url = get_settings().db_url
    
    if db_url == "sqlite:///:memory:":
        if _global_conn is None:
            _global_conn = sqlite3.connect(":memory:", check_same_thread=False)
            _global_conn.row_factory = sqlite3.Row
        return _global_conn
    else:
        db_path = db_url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

def _close_conn(conn):
    """关闭连接，如果是内存库则不关闭（为了保持数据）"""
    if get_settings().db_url != "sqlite:///:memory:":
        conn.close()

def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    _close_conn(conn)

def get_or_create_session(session_id: str) -> list[dict]:
    init_db()
    conn = _get_conn()
    conn.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
    cursor = conn.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = cursor.fetchall()
    conn.commit()
    _close_conn(conn)
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def append_message(session_id: str, role: str, content: str) -> None:
    init_db()
    conn = _get_conn()
    conn.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    _close_conn(conn)

def list_sessions() -> list[str]:
    init_db()
    conn = _get_conn()
    cursor = conn.execute("SELECT session_id FROM sessions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    _close_conn(conn)
    return [row["session_id"] for row in rows]

def get_messages(session_id: str) -> list[dict] | None:
    init_db()
    conn = _get_conn()
    # 先查会话是否存在
    session_exists = conn.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    if not session_exists:
        _close_conn(conn)
        return None  # 会话不存在，直接返回 None，路由层就会抛 404
        
    # 会话存在，查消息
    cursor = conn.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = cursor.fetchall()
    _close_conn(conn)
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def delete_session(session_id: str) -> bool:
    init_db()
    conn = _get_conn()
    # 1. 先手动删除该会话的所有消息（防患于未然）
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    # 2. 再删除会话本身
    cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    _close_conn(conn)
    return deleted

def clear_all():
    """测试用：清空数据"""
    conn = _get_conn()
    try:
        conn.executescript("DELETE FROM messages; DELETE FROM sessions;")
        conn.commit()
    except Exception:
        pass # 忽略关闭连接时的偶发错误
    finally:
        _close_conn(conn)