from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.models.user import Gender


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    birth_date: date


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
