from datetime import date, datetime

from pydantic import BaseModel

from app.models.user import Gender


class UserResponse(BaseModel):
    id: str
    nickname: str
    gender: Gender
    birth_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
