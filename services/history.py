from app.db import transactions

def get_spending_history():

    docs = list(transactions.find({}, {"_id": 0})) or []
    
    if not docs:
        return {}
    
    breakdown = {}
    
    for tx in docs:
        category = tx.get("category","Unknown")
        amount = tx.get("amount",0)

        breakdown[category] = breakdown.get(category, 0) + amount

    return breakdown