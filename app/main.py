from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import store
from app.routers import chat, sessions, study

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    yield

app = FastAPI(title="Chatbot API", lifespan=lifespan)

app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(study.router)