from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import decode_access_token
from app.db import users

# -----------------------------------
# Bearer Token Scheme
# -----------------------------------

security = HTTPBearer()


# -----------------------------------
# Get Logged-in User
# -----------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Extract the JWT token from the Authorization header,
    decode it, and return the current user.
    """

    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    from bson import ObjectId
    
    user = users.find_one(
    {
        "_id": ObjectId(payload["user_id"])
    })

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user