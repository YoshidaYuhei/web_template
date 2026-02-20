from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.account import AccountCreateRequest, AccountResponse
from app.schemas.auth import SignupResponse, TokenResponse
from app.usecase.signup_usecase import SignupUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/password", response_model=SignupResponse, status_code=201)
async def signup_with_password(
    request: AccountCreateRequest,
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> SignupResponse:
    usecase = SignupUseCase(session)
    try:
        result = await usecase.execute(email=request.email, password=request.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None

    return SignupResponse(
        account=AccountResponse(
            id=result.account_id,
            email=result.email,
            is_active=result.is_active,
            has_password=True,
            oauth_providers=[],
            passkey_count=0,
            created_at=result.created_at,
        ),
        token=TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
        ),
    )
