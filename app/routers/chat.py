from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app import store
from app.llm import call_model, call_model_stream
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message or req.message.strip() == "":
        raise HTTPException(status_code=400, detail="message 不能为空")
    
    # 1. 获取历史（不含本次用户消息）
    history = store.get_or_create_session(req.session_id)
    
    # 2. 构建发给模型的消息列表
    messages_for_model = history + [{"role": "user", "content": req.message}]
    reply = call_model(messages_for_model)
    
    # 3. 事务：同时写入用户消息和AI回复
    store.append_chat_turn(req.session_id, req.message, reply)
    
    return ChatResponse(session_id=req.session_id, reply=reply)

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if not req.message or req.message.strip() == "":
        raise HTTPException(status_code=400, detail="message 不能为空")
    
    history = store.get_or_create_session(req.session_id)
    messages_for_model = history + [{"role": "user", "content": req.message}]

    def generator():
        full_reply = ""
        for chunk in call_model_stream(messages_for_model):
            full_reply += chunk
            yield chunk
        # 流式结束后，利用事务一次性存入
        store.append_chat_turn(req.session_id, req.message, full_reply)

    return StreamingResponse(generator(), media_type="text/plain")