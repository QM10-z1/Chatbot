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
    history = store.get_or_create_session(req.session_id)
    history.append({"role": "user", "content": req.message})
    reply = call_model(history)
    store.append_message(req.session_id, "assistant", reply)
    return ChatResponse(session_id=req.session_id, reply=reply)

@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if not req.message or req.message.strip() == "":
        raise HTTPException(status_code=400, detail="message 不能为空")
    history = store.get_or_create_session(req.session_id)
    history.append({"role": "user", "content": req.message})

    def generator():
        full_reply = ""
        for chunk in call_model_stream(history):
            full_reply += chunk
            yield chunk
        store.append_message(req.session_id, "assistant", full_reply)

    return StreamingResponse(generator(), media_type="text/plain")