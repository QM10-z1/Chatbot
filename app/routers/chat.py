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
    
    # 1. 获取历史
    history = store.get_or_create_session(req.session_id)
    
    # 2. 把用户消息存进数据库！(这是你漏掉的最关键的一句)
    store.append_message(req.session_id, "user", req.message)
    
    # 3. 把用户消息加到内存 list 里，发给模型
    history.append({"role": "user", "content": req.message})
    
    # 4. 调用模型
    reply = call_model(history)
    
    # 5. 把模型的回复存进数据库
    store.append_message(req.session_id, "assistant", reply)
    
    return ChatResponse(session_id=req.session_id, reply=reply)

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if not req.message or req.message.strip() == "":
        raise HTTPException(status_code=400, detail="message 不能为空")
    
    history = store.get_or_create_session(req.session_id)
    
    # 【新增这一行】先把用户的提问存进数据库
    store.append_message(req.session_id, "user", req.message)
    
    # 把用户提问加到内存里发给模型
    history.append({"role": "user", "content": req.message})

    def generator():
        full_reply = ""
        for chunk in call_model_stream(history):
            full_reply += chunk
            yield chunk
        # 流式结束后，存机器人的回复
        store.append_message(req.session_id, "assistant", full_reply)

    return StreamingResponse(generator(), media_type="text/plain")