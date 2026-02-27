from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.staff_member import StaffMember
from app.schemas.credit import CreditBalanceResponse, CreditChargeRequest
from app.services.credit_service import add_credits

router = APIRouter(prefix="/api/v1/credits", tags=["クレジット"])


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(user: User = Depends(get_current_user)):
    return CreditBalanceResponse(credit_balance=user.credit_balance)


@router.post("/charge", response_model=CreditBalanceResponse)
async def charge_credits(
    body: CreditChargeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="チャージ金額は1以上にしてください")
    await add_credits(db, user, body.amount)
    await db.commit()
    await db.refresh(user)
    return CreditBalanceResponse(credit_balance=user.credit_balance)


@router.post("/grant/{user_id}", response_model=CreditBalanceResponse)
async def grant_credits(
    user_id: int,
    body: CreditChargeRequest,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
    await add_credits(db, target, body.amount)
    await db.commit()
    await db.refresh(target)
    return CreditBalanceResponse(credit_balance=target.credit_balance)
