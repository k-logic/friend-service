from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.staff_member import StaffMember, StaffRole
from app.services.auth_service import decode_access_token

security = HTTPBearer()


async def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Union[User, StaffMember]:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")
    account_id = int(payload["sub"])
    account_type = payload.get("type", "user")

    if account_type == "staff":
        result = await db.execute(select(StaffMember).where(StaffMember.id == account_id))
        account = result.scalar_one_or_none()
    else:
        result = await db.execute(select(User).where(User.id == account_id))
        account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="アカウントが見つかりません")
    return account


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")
    if payload.get("type") == "staff":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ユーザーアカウントでログインしてください")
    account_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == account_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="アカウントが見つかりません")
    return user


async def get_current_staff(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> StaffMember:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")
    if payload.get("type") != "staff":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="スタッフ権限が必要です")
    account_id = int(payload["sub"])
    result = await db.execute(select(StaffMember).where(StaffMember.id == account_id))
    staff = result.scalar_one_or_none()
    if staff is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="アカウントが見つかりません")
    return staff


async def get_current_admin(
    staff: StaffMember = Depends(get_current_staff),
) -> StaffMember:
    if staff.role != StaffRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="管理者権限が必要です")
    return staff
