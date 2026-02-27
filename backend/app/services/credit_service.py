from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


async def deduct_credits(db: AsyncSession, account: Account, amount: int) -> None:
    if account.credit_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"クレジットが不足しています（残高: {account.credit_balance}, 必要: {amount}）",
        )
    account.credit_balance -= amount
    db.add(account)


async def add_credits(db: AsyncSession, account: Account, amount: int) -> None:
    account.credit_balance += amount
    db.add(account)
