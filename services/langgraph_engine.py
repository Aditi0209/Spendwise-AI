from langgraph.graph import StateGraph
from services.state import SpendState

from services.parser import parse_transactions
from agents.profile_agent import get_profile
from agents.history_agent import get_history
from services.rag import retrieve_context
from agents.allocation_agent import run_allocation

from langfuse import get_client
from groq import Groq
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("spendwise.langgraph")

# Initialize clients only if API keys exist; otherwise leave None and handle later
_GROQ_KEY = os.getenv("GROQ_API_KEY")
_LANGFUSE_KEY = os.getenv("LANGFUSE_API_KEY")

try:
    langfuse = get_client() if _LANGFUSE_KEY else None
except Exception as e:
    logger.warning(f"Langfuse client init failed: {e}")
    langfuse = None

try:
    client = Groq(api_key=_GROQ_KEY) if _GROQ_KEY else None
except Exception as e:
    logger.warning(f"Groq client init failed: {e}")
    client = None

# -------------------------
# NODE 1: PARSE
# -------------------------
def parse_node(state):
    text = state.get("text", "")
    transactions = parse_transactions(text)

    return {
        "transactions": transactions
    }


# -------------------------
# NODE 2: BREAKDOWN
# -------------------------
def breakdown_node(state):
    transactions = state.get("transactions", [])

    breakdown = {}

    for t in transactions:
        cat = t.get("category", "Unknown")
        amt = t.get("amount", 0)
        breakdown[cat] = breakdown.get(cat, 0) + amt

    return {
        "breakdown": breakdown
    }


# -------------------------
# NODE 3: PROFILE
# -------------------------
def profile_node(state):
    return {
        "profile": get_profile() or {}
    }


# -------------------------
# NODE 4: HISTORY
# -------------------------
def history_node(state):
    return {
        "history": get_history() or {}
    }


# -------------------------
# NODE 5: RAG
# -------------------------
def rag_node(state):
    breakdown_keys = list(state.get("breakdown", {}).keys())

    query = " ".join(breakdown_keys) if breakdown_keys else "budget savings investment financial advice"

    return {
        "rag_context": retrieve_context(query) or []
    }


# -------------------------
# JOIN NODE (IMPORTANT FIX)
# -------------------------
def join_node(state):
    return {
        "transactions": state.get("transactions"),
        "breakdown": state.get("breakdown"),
        "profile": state.get("profile"),
        "history": state.get("history"),
        "rag_context": state.get("rag_context"),
    }


# -------------------------
# NODE 6: ALLOCATION
# -------------------------
def allocation_node(state):
    return {
        "allocation": run_allocation(
            state.get("profile"),
            state.get("breakdown")
        )
    }


# -------------------------
# NODE 7: ADVISOR (LLM + LANGFUSE)
# -------------------------
def advisor_node(state):

    profile = state.get("profile", {})
    history = state.get("history", {})
    breakdown = state.get("breakdown", {})
    allocation = state.get("allocation", {})
    context = state.get("rag_context", [])

    prompt = f"""
You are an expert financial advisor.

Profile: {profile}
History: {history}
Breakdown: {breakdown}
Allocation: {allocation}
Context: {context}

Give insights, risks, savings plan.
"""

    output = None

    # If LLM client is not configured, return a safe fallback message
    if client is None:
        logger.warning("Groq client not configured; returning fallback advice.")
        output = (
            "LLM not configured. Fallback advice: follow basic budgeting rules, build an emergency fund, "
            "and track discretionary spending."
        )
        return {"final_advice": output}

    # Attempt to trace and generate via Langfuse + Groq; handle failures gracefully
    try:
        if langfuse:
            with langfuse.start_as_current_observation(
                as_type="span",
                name="financial-advisor"
            ) as span:
                span.update(input={"profile": profile, "history": history, "breakdown": breakdown})

                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="llm-advisor",
                    model="llama-3.3-70b-versatile"
                ) as generation:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                    )
                    output = response.choices[0].message.content
                    generation.update(input=prompt, output=output)

                span.update(output={"final_advice": output})
        else:
            # No langfuse, but Groq client exists — still attempt LLM call
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            output = response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM/langfuse error in advisor_node: {e}")
        output = (
            "LLM error occurred. Fallback advice: follow basic budgeting rules, build an emergency fund, "
            "and track discretionary spending."
        )

    return {"final_advice": output}


# -------------------------
# GRAPH SETUP
# -------------------------
graph = StateGraph(SpendState)

graph.add_node("parse", parse_node)
graph.add_node("breakdown", breakdown_node)
graph.add_node("profile", profile_node)
graph.add_node("history", history_node)
graph.add_node("rag", rag_node)
graph.add_node("join", join_node)
graph.add_node("allocation", allocation_node)
graph.add_node("advisor", advisor_node)

graph.set_entry_point("parse")

# Flow
graph.add_edge("parse", "breakdown")

# Parallel branches
graph.add_edge("breakdown", "profile")
graph.add_edge("breakdown", "history")
graph.add_edge("breakdown", "rag")

# JOIN FIX (CRITICAL)
graph.add_edge("profile", "join")
graph.add_edge("history", "join")
graph.add_edge("rag", "join")

# Continue pipeline
graph.add_edge("join", "allocation")
graph.add_edge("allocation", "advisor")

graph.set_finish_point("advisor")

app = graph.compile()


# -------------------------
# RUN FUNCTION (FIXED)
# -------------------------
def run_graph(text: str):

    result = app.invoke({
        "text": text,
    })
    return result