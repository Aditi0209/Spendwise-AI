from services.rag import retrieve_context
from services.llm import client
from app.db import profiles
from services.history import get_spending_history
from services.allocation import allocate
from services.utils import compute_total_spending
import logging


logger = logging.getLogger("spendwise")

def generate_advice(transactions):
    
    if not transactions:
        return {
            "error": "No transactions provided"
        }

    profile = profiles.find_one({}, {"_id": 0})

    if not profile:
        return {
            "error": "Please create a profile first using /profile endpoint"
        }

    history = get_spending_history() or {}

    allocation = allocate(profile, history)

    total_spend = compute_total_spending(transactions)

    breakdown = {}

    for t in transactions:

        category = t.get("category","Unknown")
        amount = t.get("amount",0)
        breakdown[category] = breakdown.get(category, 0)+ amount
        
    if not breakdown:
        return {
            "error": "Could not compute spending breakdown"
        }
          
    age = profile.get("age",0)
    goal = profile.get("goal","general") 
    risk = profile.get("risk_appetite","medium")

    largest_category = (
        max(breakdown, key=breakdown.get)
        if breakdown else "unknown"
    )
    
    query = f"""
        Age: {age}
        Goal: {goal}
        Risk: {risk}
        Top spending: {largest_category}
    """

    try:
        context = retrieve_context(query) or [
            "Follow basic budgeting principles and maintain financial discipline."
        ]
    except Exception as e:
        logger.error(f"RAG error: {e}")
        context = ["General financial rules apply."]

    prompt = f"""
You are a strict financial decision system.

Based on the input, output ONLY ONE PRIMARY ACTION.

Allowed actions:
- reduce_discretionary_spending
- invest_surplus
- build_emergency_fund
- balanced_budget
- no_action_needed

Rules:
- Choose ONLY ONE most important action
- Do NOT give explanations
- Do NOT give paragraphs
- Output ONLY the label

Profile: {profile}
History: {history}
Breakdown: {breakdown}
Allocation: {allocation}
Context: {context}

FINAL ANSWER:
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        result = response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM error: {e}")
        result = "Unable to generate advice due to LLM error."
    

    return {
        "profile": profile,
        "total_spend": total_spend,
        "breakdown": breakdown,
        "historical_spending": history,
        "asset_allocation": allocation,
        "retrieved_context": context,
        "advice": result
    }
    
    
    
