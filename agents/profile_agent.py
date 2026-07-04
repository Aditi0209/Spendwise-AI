from app.db import profiles

def get_profile():
    return profiles.find_one({}, {"_id": 0})