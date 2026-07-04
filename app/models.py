from pydantic import BaseModel

class ParseRequest(BaseModel):
    text:str

class UserProfile(BaseModel):
    name: str
    age: int
    monthly_income: float
    risk_appetite: str
    goal: str