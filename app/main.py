from fastapi import FastAPI
from app.routes import router
from services.rag import load_knowledge
load_knowledge()
app = FastAPI()

app.include_router(router)

@app.get("/")
def home():
    return {"message":"SpendWise RAG"}

@app.on_event("startup")
def startup_event():
    load_knowledge()