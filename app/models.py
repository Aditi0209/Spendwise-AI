from pydantic import BaseModel

# Authentication Models

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ParseRequest(BaseModel):
    text: str

class UserProfile(BaseModel):
    name: str
    age: int
    monthly_income: float
    monthly_spend: float = 0
    risk_appetite: str
    goal: str
    
class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str