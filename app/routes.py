from fastapi import APIRouter
from app.models import ParseRequest
from services.parser import parse_transactions
from services.advisor import generate_advice
from app.models import UserProfile
from app.db import profiles
from services.history import get_spending_history
from app.db import transactions

router = APIRouter()

@router.post("/parse")
def parse(request: ParseRequest):

    parsed_transactions = parse_transactions(request.text)
    
    for tx in parsed_transactions:
        transactions.insert_one(tx.copy())

    return {
        "transactions": parsed_transactions
    }

from services.langgraph_engine import run_graph

@router.post("/advisor")
async def advisor(request: ParseRequest):

    return run_graph(request.text)

@router.post("/profile")
def create_profile(profile: UserProfile):

    profiles.delete_many({})

    profiles.insert_one(profile.dict())

    return {
        "message": "Profile saved"
    }
    
@router.get("/profile")
def get_profile():

    profile = profiles.find_one({}, {"_id": 0})

    return profile

@router.get("/history-summary")
def history_summary():

    return get_spending_history()

