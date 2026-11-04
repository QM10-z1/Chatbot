from fastapi import APIRouter, HTTPException
from app import store

router = APIRouter(tags=["Sessions"])

@router.get("/sessions")
def get_sessions():
    return {"sessions": store.list_sessions()}

@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str):
    messages = store.get_messages(session_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session_id": session_id, "messages": messages}

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if not store.delete_session(session_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session_id": session_id, "deleted": True}