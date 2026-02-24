from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.schemas.account import AccountCreateRequest, AccountResponse
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    SignupResponse,
    TokenResponse,
)
from app.usecase.login_usecase import LoginUseCase
from app.usecase.logout_usecase import LogoutUseCase
from app.usecase.refresh_usecase import RefreshUseCase
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


@router.post("/login/password", response_model=LoginResponse)
async def login_with_password(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> LoginResponse:
    usecase = LoginUseCase(session)
    try:
        result = await usecase.execute(email=request.email, password=request.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None

    return LoginResponse(
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> TokenResponse:
    usecase = RefreshUseCase(session)
    try:
        result = await usecase.execute(refresh_token=request.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/logout", status_code=204)
async def logout(
    request: RefreshRequest,
    _current_user: Account = Depends(get_current_user),  # noqa: B008
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> Response:
    usecase = LogoutUseCase(session)
    await usecase.execute(refresh_token=request.refresh_token)
    return Response(status_code=204)
