from fastapi import FastAPI
from app.routers import chat, sessions

app = FastAPI(title="Chatbot API")

# 把拆分出去的模块挂载回主 app
app.include_router(chat.router)
app.include_router(sessions.router)
