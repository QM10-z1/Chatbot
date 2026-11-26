from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import store
from app.routers import chat, sessions, study
from fastapi.staticfiles import StaticFiles
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    yield

app = FastAPI(title="Chatbot API", lifespan=lifespan)

app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(study.router)

static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")