from app.db import profiles


def get_profile(user_id: str):

    return profiles.find_one(

        {
            "user_id": user_id
        },

        {
            "_id": 0
        }

    ) or {}