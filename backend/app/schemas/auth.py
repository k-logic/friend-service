from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountResponse(BaseModel):
    id: int
    email: str
    display_name: str
    credit_balance: int
    role: str
    status: str
    avatar_url: str | None

    model_config = {"from_attributes": True}
