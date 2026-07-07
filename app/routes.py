from fastapi import APIRouter, HTTPException, status, Depends
from app.dependencies import get_current_user

from app.models import (
    ParseRequest,
    UserProfile,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)

from app.db import (
    users,
    profiles,
    transactions,
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)

from services.parser import parse_transactions

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

# REGISTER

@router.post("/register")
def register(request: RegisterRequest):

    existing_user = users.find_one(
        {
            "email": request.email
        }
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = {

        "username": request.username,

        "email": request.email,

        "password": hash_password(request.password)

    }

    users.insert_one(user)

    return {
        "message": "User registered successfully"
    }

# LOGIN 
@router.post("/login",response_model=TokenResponse)
def login(request: LoginRequest):

    user = users.find_one(
        {
            "email": request.email
        }
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        request.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "user_id": str(user["_id"]),
            "email": user["email"]
        }
    )

    return TokenResponse(
        access_token=token
    )
    
# PARSE

@router.post("/parse")
def parse(request: ParseRequest,current_user=Depends(get_current_user)):
    parsed_transactions = parse_transactions(request.text)
    for tx in parsed_transactions:
        tx["user_id"] = str(current_user["_id"])
        transactions.insert_one(tx)

    return {
        "transactions": parsed_transactions
    }


# ADVISOR
@router.post("/advisor")
async def advisor(request: ParseRequest,current_user=Depends(get_current_user)):

    result = run_graph(request.text,str(current_user["_id"]))
    for tx in result.get("transactions", []):
        tx_data = dict(tx)
        tx_data["user_id"] = str(current_user["_id"])
        transactions.insert_one(tx_data)

    return result

# PROFILE

@router.post("/profile")
def create_profile(
    profile: UserProfile,
    current_user=Depends(get_current_user)
):

    profile_data = profile.model_dump()

    profile_data["user_id"] = str(current_user["_id"])

    profiles.update_one(
        {
            "user_id": str(current_user["_id"])
        },
        {
            "$set": profile_data
        },
        upsert=True
    )

    return {
        "message": "Profile saved successfully"
    }

@router.get("/profile")
def get_profile(
    current_user=Depends(get_current_user)
):

    profile = profiles.find_one(
        {
            "user_id": str(current_user["_id"])
        },
        {
            "_id": 0
        }
    )

    return profile or {}

# HISTORY

@router.get("/history-summary")
def history_summary(
    current_user=Depends(get_current_user)
):

    return get_spending_history(
        str(current_user["_id"])
    )
    
# TRANSACTIONS

@router.get("/transactions")
def get_transactions(
    current_user=Depends(get_current_user)
):

    return list(

        transactions.find(

            {
                "user_id": str(current_user["_id"])
            },

            {
                "_id": 0
            }

        )

    )
# HEALTH

@router.get("/health")
def health():

    return {
        "fastapi": "ok",
        "mongodb": "ok",
        "langgraph": "ok",
        "llm": "ok",
    }