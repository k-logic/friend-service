from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin, get_current_staff
from app.models.user import User, UserStatus
from app.models.staff_member import StaffMember
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
    user_status: str | None = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    staff: StaffMember = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))
    if display_name:
        stmt = stmt.where(User.display_name.ilike(f"%{display_name}%"))
    if user_status:
        stmt = stmt.where(User.status == user_status)
    stmt = stmt.order_by(User.id.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: AdminUserCreateRequest,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に登録されています")

    user = User(
        email=body.email,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=AdminUserResponse)
async def update_user_status(
    user_id: int,
    body: AdminUserStatusUpdate,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
    user.status = UserStatus(body.status)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/count-by-status", response_model=list[UserCountByStatus])
async def count_by_status(
    staff: StaffMember = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User.status, func.count(User.id)).group_by(User.status)
    result = await db.execute(stmt)
    return [UserCountByStatus(status=row[0].value, count=row[1]) for row in result.all()]
