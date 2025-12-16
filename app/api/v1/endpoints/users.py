from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_account
from app.db.session import get_db
from app.models.account import Account
from app.query.user_query import UserQuery
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user_query = UserQuery(db)
    user = await user_query.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)
