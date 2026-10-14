# Spendwise-AI

An AI-powered personal finance assistant. Paste unstructured transaction text (e.g. "Zomato 250, cab 180") and get a categorized spending breakdown, a rule-based asset allocation and personalized financial advice.

## Features

- **LLM transaction parsing:** converts free-form text into structured JSON (amount, category, merchant) using Llama 3.3 70B on Groq.
- **LangGraph workflow:** a multi-node pipeline with shared state; profile lookup, spending history and RAG retrieval run in parallel.
- **RAG:** relevant financial tips are retrieved from a ChromaDB knowledge base and given to the advisor as context.
- **Rule-based asset allocation:** deterministic split based on income, risk appetite, age, goal and actual spending.
- **AI advisor:** the LLM combines profile, history, breakdown, allocation and retrieved tips into insights, risks and a savings plan.
- **Authentication:** JWT-based register/login with bcrypt password hashing; all data is scoped to the logged-in user.
- **Observability:** Langfuse traces the advisor's LLM call (input, output, model, latency).

## How It Works

```
Text input
   │
   ▼
parse (LLM) ──► breakdown ──┬─► profile (MongoDB) ──┐
                            ├─► history (MongoDB) ──┼─► join ─► allocation (rules) ─► advisor (LLM + RAG context)
                            └─► rag (ChromaDB) ─────┘
```

Only the **parse** and **advisor** nodes call the LLM. The other nodes are database lookups, retrieval, or plain Python logic.

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, Pydantic |
| Database | MongoDB (PyMongo) |
| Vector store | ChromaDB (default embeddings) |
| Orchestration | LangGraph |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Observability | Langfuse |
| Auth | JWT (python-jose), bcrypt (passlib) |

## Project Structure

```
app/        FastAPI app, routes, models, auth, DB connection
services/   parser, rag, allocation, history, llm, LangGraph engine
agents/     profile, history, rag and allocation nodes
data/       financial_tips.txt (RAG knowledge base)
```

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root:
   ```
   MONGO_URI=your_mongodb_connection_string
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_long_random_secret
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
3. Run the server (the knowledge base loads into ChromaDB on first startup):
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open the interactive API docs at `http://127.0.0.1:8000/docs`.

## Design Decisions

- **Asset allocation is rule-based, not LLM-generated:** financial numbers should be deterministic and explainable. The LLM only explains and advises on top of them.
- **Deterministic graph instead of autonomous agents:** each step is fixed, which makes the workflow predictable, cheaper and easier to debug.

## Known Limitations and Future Work

- RAG retrieval quality has not been formally evaluated (planned: recall@k and RAGAS).
- Only the advisor LLM call is traced in Langfuse; the parse step is not yet instrumented.
- LLM output from the parser is not yet validated against a schema or retried on invalid JSON.
- Submitting the same text twice creates duplicate transactions (idempotency is a planned improvement).
- Blocking LLM and database calls inside `async` routes should be moved to async clients.
