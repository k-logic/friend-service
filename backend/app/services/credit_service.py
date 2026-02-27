from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def deduct_credits(db: AsyncSession, user: User, amount: int) -> None:
    if user.credit_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"クレジットが不足しています（残高: {user.credit_balance}, 必要: {amount}）",
        )
    user.credit_balance -= amount
    db.add(user)


async def add_credits(db: AsyncSession, user: User, amount: int) -> None:
    user.credit_balance += amount
    db.add(user)
