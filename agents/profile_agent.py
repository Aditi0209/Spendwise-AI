from app.db import profiles


def get_profile(user_id: str = None):
    # Single-user mode: ignore user_id and return the stored profile
    return profiles.find_one({}, {"_id": 0})
