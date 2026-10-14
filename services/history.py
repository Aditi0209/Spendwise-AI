from app.db import transactions, analysis_history
from datetime import datetime

def get_spending_history(user_id: str):

    docs = list(

        transactions.find(

            {
                "user_id": user_id
            },

            {
                "_id": 0
            }

        )

    )

    if not docs:
        return {}

    breakdown = {}

    for tx in docs:

        category = tx.get("category", "Unknown")

        amount = tx.get("amount", 0)

        breakdown[category] = (
            breakdown.get(category, 0)
            + amount
        )

    return breakdown

def save_analysis(user_id: str, breakdown: dict, allocation: dict, advice: str):
    total_spending = sum(breakdown.values())

    analysis = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "total_spending": total_spending,
        "breakdown": breakdown,
        "allocation": allocation,
        "final_advice": advice,
    }

    analysis_history.insert_one(analysis)
    
def get_analysis_history(user_id: str):

    analyses = list(

        analysis_history.find(

            {
                "user_id": user_id
            },

            {
                "_id": 0
            }

        ).sort("timestamp", -1)

    )

    return analyses