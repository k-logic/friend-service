from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.account import Account, AccountRole, AccountStatus
from app.schemas.admin import (
    AdminUserCreateRequest,
    AdminUserResponse,
    AdminUserStatusUpdate,
    UserCountByStatus,
)
from app.services.auth_service import hash_password

router = APIRouter(prefix="/api/v1/admin/users", tags=["管理: ユーザ管理"])


@router.get("", response_model=list[AdminUserResponse])
async def search_users(
    email: str | None = Query(None),
    display_name: str | None = Query(None),
    role: str | None = Query(None),
    user_status: str | None = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Account)
    if email:
        stmt = stmt.where(Account.email.ilike(f"%{email}%"))
    if display_name:
        stmt = stmt.where(Account.display_name.ilike(f"%{display_name}%"))
    if role:
        stmt = stmt.where(Account.role == role)
    if user_status:
        stmt = stmt.where(Account.status == user_status)
    stmt = stmt.order_by(Account.id.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: AdminUserCreateRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Account).where(Account.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に登録されています")

    account = Account(
        email=body.email,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
        role=AccountRole(body.role),
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.patch("/{account_id}/status", response_model=AdminUserResponse)
async def update_user_status(
    account_id: int,
    body: AdminUserStatusUpdate,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="アカウントが見つかりません")
    account.status = AccountStatus(body.status)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/count-by-status", response_model=list[UserCountByStatus])
async def count_by_status(
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Account.status, func.count(Account.id)).group_by(Account.status)
    result = await db.execute(stmt)
    return [UserCountByStatus(status=row[0].value, count=row[1]) for row in result.all()]
