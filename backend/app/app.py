from fastapi import FastAPI , APIRouter
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router 
from backend.core.chatbot import build_graph

app = FastAPI(
    title="misl" ,
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    app.state.bot = await build_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)
