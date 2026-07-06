from fastapi import APIRouter
from app.models import ParseRequest
from services.parser import parse_transactions
from services.advisor import generate_advice
from app.models import UserProfile
from app.db import profiles

# from app.auth import (
#     create_session,
#     get_current_user,
#     hash_password,
#     verify_password,
# )
# from app.db import profiles, sessions, transactions, users
# from app.models import LoginRequest, ParseRequest, SignupRequest, UserProfile
from app.db import transactions
from services.history import get_spending_history
from services.langgraph_engine import run_graph

router = APIRouter()


def default_profile(name: str = "") -> dict:
    return {
        "name": name,
        "age": 0,
        "monthly_income": 0,
        "monthly_spend": 0,
        "risk_appetite": "Medium",
        "goal": "",
    }


# @router.post("/auth/signup")
# def signup(request: SignupRequest):
#     email = request.email.strip().lower()

#     if not email or not request.password:
#         raise HTTPException(status_code=400, detail="Email and password are required")

#     if users.find_one({"email": email}):
#         raise HTTPException(status_code=400, detail="Email already registered")

#     users.insert_one(
#         {
#             "email": email,
#             "name": request.name.strip(),
#             "password_hash": hash_password(request.password),
#         }
#     )

#     profiles.insert_one({"user_id": email, **default_profile(request.name.strip())})

#     token = create_session(email)

#     return {
#         "token": token,
#         "user": {"email": email, "name": request.name.strip()},
#     }


# @router.post("/auth/login")
# def login(request: LoginRequest):
#     email = request.email.strip().lower()
#     user = users.find_one({"email": email})

#     if not user or not verify_password(request.password, user["password_hash"]):
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     token = create_session(email)

#     return {
#         "token": token,
#         "user": {"email": email, "name": user.get("name", "")},
#     }


# @router.get("/auth/me")
# def me(user: dict = Depends(get_current_user)):
#     return user


# @router.post("/auth/logout")
# def logout(authorization: str = Header(default=None)):
#     if authorization and authorization.startswith("Bearer "):
#         sessions.delete_one({"token": authorization[7:]})

#     return {"message": "Logged out"}


@router.post("/parse")
def parse(request: ParseRequest):
    parsed_transactions = parse_transactions(request.text)
    
    for tx in parsed_transactions:
        transactions.insert_one(tx.copy())

    return {"transactions": parsed_transactions}


@router.post("/advisor")
async def advisor(request: ParseRequest):
    # user_id = user["email"]
    result = run_graph(request.text)

    for tx in result.get("transactions", []):
        transactions.insert_one(tx.copy())
    return result


@router.post("/profile")
def create_profile(profile: UserProfile):
    try:
        profiles.replace_one({}, profile.model_dump(), upsert=True)
        return {"message": "Profile saved"}
    except Exception as e:
        # Log and return error response
        return {"error": f"Could not save profile: {e}"}


@router.get("/profile")
def get_profile():
    # user_id = user["email"]
    try:
        profile = profiles.find_one({}, {"_id": 0})
        return profile or {}
    except Exception as e:
        return {"error": f"Could not retrieve profile: {e}"}


@router.get("/history-summary")
def history_summary():
    return get_spending_history()


@router.get("/transactions")
def get_transactions():
    return list(transactions.find({}, {"_id": 0}))


@router.get("/health")
def health():
    return {
        "fastapi": "ok",
        "mongodb": "ok",
        "langgraph": "ok",
        "llm": "ok",
    }
