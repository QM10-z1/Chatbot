from contextlib import contextmanager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models import Base, Session, Message

# 初始化引擎
settings = get_settings()
db_url = settings.db_url

# SQLite 需要 check_same_thread=False 才能在 FastAPI 的多线程下使用
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """启动时自动建表（不会删除旧表，只会创建缺失的表）"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """提供数据库会话上下文，保证自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_session(session_id: str) -> list[dict]:
    with get_db() as db:
        # 查找会话
        session_obj = db.get(Session, session_id)
        if not session_obj:
            session_obj = Session(session_id=session_id)
            db.add(session_obj)
            db.commit()
        
        # 通过 relationship 直接获取该会话的所有消息，按时间排序
        msgs = sorted(session_obj.messages, key=lambda m: m.id)
        return [{"role": m.role, "content": m.content} for m in msgs]

def append_chat_turn(session_id: str, user_msg: str, ai_reply: str) -> None:
    """
    【作业要求:同一事务】将用户消息和AI回复作为一个原子操作同时写入。
    如果 AI 生成失败，或者写入过程中抛出异常，整个事务回滚，不会留下半轮对话。
    """
    with get_db() as db:
        try:
            # 确保会话存在
            if not db.get(Session, session_id):
                db.add(Session(session_id=session_id))
                db.flush() # 将新会话 ID 刷入数据库，但不提交事务

            # 插入两条消息
            msg1 = Message(session_id=session_id, role="user", content=user_msg)
            msg2 = Message(session_id=session_id, role="assistant", content=ai_reply)
            db.add_all([msg1, msg2])
            
            db.commit() # 一次性提交，保证事务完整性
        except Exception as e:
            db.rollback() # 一旦出错，回滚事务
            raise e

def list_sessions() -> list[str]:
    with get_db() as db:
        stmt = select(Session.session_id).order_by(Session.created_at.desc())
        return [row[0] for row in db.execute(stmt).all()]

def get_messages(session_id: str) -> list[dict] | None:
    with get_db() as db:
        session_obj = db.get(Session, session_id)
        if not session_obj:
            return None
        msgs = sorted(session_obj.messages, key=lambda m: m.id)
        return [{"role": m.role, "content": m.content} for m in msgs]

def delete_session(session_id: str) -> bool:
    with get_db() as db:
        session_obj = db.get(Session, session_id)
        if not session_obj:
            return False
        # 因为配置了 cascade="all, delete-orphan"，删除会话会自动级联删除消息
        db.delete(session_obj)
        db.commit()
        return True

def clear_all():
    with get_db() as db:
        # 仅用于测试清理
        db.query(Message).delete()
        db.query(Session).delete()
        db.commit()

def search_messages(session_id: str, keyword: str) -> list[dict] | None:
    with get_db() as db:
        session_obj = db.get(Session, session_id)
        if not session_obj:
            return None
        
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .where(Message.content.contains(keyword))
            .order_by(Message.id.asc())
        )
        results = db.execute(stmt).scalars().all()
        return [{"role": m.role, "content": m.content} for m in results]