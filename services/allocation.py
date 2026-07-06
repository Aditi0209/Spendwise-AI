def allocate(profile, spending):

    if not profile or "monthly_income" not in profile:
        return {
            "note": "Save your profile first to get asset allocation recommendations"
        }

    income = profile["monthly_income"]
    risk = profile["risk_appetite"].lower()
    goal = profile["goal"].lower()

    total_spent = sum(spending.values())

    # ✅ real savings capacity
    savings_capacity = income - total_spent

    # if negative → no investment possible
    if savings_capacity <= 0:
        return {
            "emergency_fund": 0,
            "mutual_funds": 0,
            "stocks": 0,
            "note": "No savings capacity due to overspending"
        }

    # -------------------------
    # BASE ALLOCATION (SAFE)
    # -------------------------
    if risk == "low":
        allocation = {"emergency_fund": 60, "fixed_deposit": 30, "mutual_funds": 10}

    elif risk == "medium":
        allocation = {"emergency_fund": 40, "mutual_funds": 40, "stocks": 20}

    else:
        allocation = {"emergency_fund": 20, "mutual_funds": 40, "stocks": 40}

    # -------------------------
    # AGE ADJUSTMENT
    # -------------------------
    if profile["age"] < 30:
        allocation["stocks"] = allocation.get("stocks", 0) + 10
        allocation["emergency_fund"] -= 10

    elif profile["age"] > 45:
        allocation["emergency_fund"] += 10
        if "stocks" in allocation:
            allocation["stocks"] -= 10

    # -------------------------
    # GOAL ADJUSTMENT
    # -------------------------
    if "wealth" in goal:
        allocation["stocks"] += 10
    elif "house" in goal:
        allocation["fixed_deposit"] = allocation.get("fixed_deposit", 0) + 10
    elif "retirement" in goal:
        allocation["mutual_funds"] += 10

    # -------------------------
    # NORMALIZE (VERY IMPORTANT FIX)
    # -------------------------
    total_pct = sum(allocation.values())

    for k in allocation:
        allocation[k] = max(allocation[k], 0)

    # convert to actual money
    recommendation = {}
    for asset, pct in allocation.items():
        recommendation[asset] = round(
            savings_capacity * pct / total_pct,
            2
        )

    return recommendation