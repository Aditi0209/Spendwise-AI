def compute_total_spending(transactions):
    return sum(t.get("amount", 0) for t in transactions)