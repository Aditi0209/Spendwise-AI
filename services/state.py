from typing import TypedDict, List, Dict, Any

class SpendState(TypedDict):
    text: str
    transactions: List[Dict]
    breakdown: Dict[str, float]
    profile: Dict[str, Any]
    history: Dict[str, float]
    rag_context: List[str]
    allocation: Dict[str, float]
    final_advice: str
    
class SpendState(TypedDict, total=False):
    text: str
    transactions: list
    breakdown: dict

    profile: dict
    history: dict
    rag_context: list

    allocation: dict
    final_advice: str