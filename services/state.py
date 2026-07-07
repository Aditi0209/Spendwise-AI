from typing import TypedDict, List, Dict, Any

class SpendState(TypedDict):
    text: str
    user_id: str
    transactions: List[Dict]
    breakdown: Dict[str, float]
    profile: Dict[str, Any]
    history: Dict[str, float]
    rag_context: List[str]
    allocation: Dict[str, float]
    final_advice: str