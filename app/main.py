from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from services.rag import load_knowledge


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts.
    Loads the RAG knowledge base.
    """
    load_knowledge()
    yield


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

# Register all API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Backend running"
    }