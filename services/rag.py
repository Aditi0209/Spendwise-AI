import chromadb
import os
import time

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="financial_knowledge"
)

FILE_PATH = "data/financial_tips.txt"

# store last loaded timestamp in memory
_last_loaded_time = None


def get_file_modified_time():
    return os.path.getmtime(FILE_PATH)


def is_initialized():
    try:
        result = collection.get(ids=["__init_marker__"])
        return len(result["ids"]) > 0
    except:
        return False


def load_knowledge(force_reload=False):

    global _last_loaded_time

    # Skip if already initialized in ChromaDB
    if not force_reload and is_initialized():
        print("[RAG] Already loaded in ChromaDB. Skipping reload.")
        return

    print("[RAG] Loading knowledge base...")

    # Clear old data only if manual reload
    if force_reload and collection.count() > 0:
        ids = collection.get()["ids"]
        collection.delete(ids=ids)

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[str(i)]
        )

    # permanent marker
    collection.add(
        documents=["initialized"],
        ids=["__init_marker__"]
    )

    _last_loaded_time = time.time()

    print(f"[RAG] Loaded {len(chunks)} chunks once.")


def retrieve_context(query):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [])

    if not docs or not docs[0]:
        return []

    return docs[0]

