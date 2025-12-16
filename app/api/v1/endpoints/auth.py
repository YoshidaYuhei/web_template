from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.command.account_command import AccountCommand
from app.command.user_command import UserCommand
from app.core.deps import get_current_account
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
)
from app.db.session import get_db
from app.models.account import Account
from app.query.account_query import AccountQuery
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    account_query = AccountQuery(db)
    existing = await account_query.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    account_command = AccountCommand(db)
    hashed_password = get_password_hash(request.password)
    refresh_token, expires_at = create_refresh_token()

    account = await account_command.create(
        email=request.email,
        hashed_password=hashed_password,
        refresh_token=refresh_token,
        refresh_token_expires_at=expires_at,
    )

    user_command = UserCommand(db)
    await user_command.create(
        account_id=account.id,
        nickname=request.nickname,
        gender=request.gender,
        birth_date=request.birth_date,
    )

    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    account_query = AccountQuery(db)
    account = await account_query.get_by_email(request.email)

    if not account or not verify_password(request.password, account.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )

    account_command = AccountCommand(db)
    refresh_token, expires_at = create_refresh_token()
    await account_command.update_refresh_token(
        account_id=account.id,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> None:
    account_command = AccountCommand(db)
    await account_command.clear_refresh_token(current_account.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    account_query = AccountQuery(db)
    account = await account_query.get_by_refresh_token(request.refresh_token)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if not verify_refresh_token(account.refresh_token_expires_at):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    account_command = AccountCommand(db)
    new_refresh_token, expires_at = create_refresh_token()
    await account_command.update_refresh_token(
        account_id=account.id,
        refresh_token=new_refresh_token,
        expires_at=expires_at,
    )

    access_token = create_access_token(data={"sub": account.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
