from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account, AccountRole
from app.services.auth_service import decode_access_token

security = HTTPBearer()


async def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Account:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")
    account_id = int(payload["sub"])
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="アカウントが見つかりません")
    return account


async def get_current_staff(account: Account = Depends(get_current_account)) -> Account:
    if account.role not in (AccountRole.staff, AccountRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="スタッフ権限が必要です")
    return account


async def get_current_admin(account: Account = Depends(get_current_account)) -> Account:
    if account.role != AccountRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="管理者権限が必要です")
    return account
