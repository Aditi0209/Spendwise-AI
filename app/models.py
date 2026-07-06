from pydantic import BaseModel


class ParseRequest(BaseModel):
    text: str


# class SignupRequest(BaseModel):
#     email: str
#     password: str
#     name: str = ""


# class LoginRequest(BaseModel):
#     email: str
#     password: str


class UserProfile(BaseModel):
    name: str = ""
    age: int = 0
    monthly_income: float = 0
    monthly_spend: float = 0
    risk_appetite: str = "Medium"
    goal: str = ""
