from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account
from app.models.account import Account
from app.schemas.auth import AccountResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import authenticate, create_access_token, hash_password

router = APIRouter(prefix="/api/v1/auth", tags=["認証"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Account).where(Account.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に登録されています")

    account = Account(
        email=body.email,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)

    token = create_access_token(account.id, account.role.value)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    account = await authenticate(db, body.email, body.password)
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="メールアドレスまたはパスワードが正しくありません")

    token = create_access_token(account.id, account.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AccountResponse)
async def get_me(account: Account = Depends(get_current_account)):
    return account
