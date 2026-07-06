from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import router
from services.rag import load_knowledge

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts and shuts down.
    Initialize shared resources here.
    """

    # Initialize RAG knowledge base
    load_knowledge()

    # Future startup tasks:
    # connect_mongodb()
    # initialize_langfuse()
    # initialize_vector_store()

    yield

    # Future cleanup tasks:
    # close_mongodb()
    # shutdown_vector_store()


app = FastAPI(
    title="SpendWise AI",
    description="AI-powered Financial Orchestration System",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:

    @app.get("/", tags=["Health"])
    async def health_check():
        return {
            "status": "running",
            "service": "SpendWise AI",
            "version": "1.0.0",
        }