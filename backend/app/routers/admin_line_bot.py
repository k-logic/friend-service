from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.account import Account
from app.models.line_bot_account import LineBotAccount
from app.schemas.admin import LineBotAccountCreateRequest, LineBotAccountResponse, LineBotAccountUpdateRequest

router = APIRouter(prefix="/api/v1/admin/line-bot", tags=["管理: LINE Bot"])


@router.get("", response_model=list[LineBotAccountResponse])
async def list_line_bots(
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LineBotAccount).order_by(LineBotAccount.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=LineBotAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_line_bot(
    body: LineBotAccountCreateRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(LineBotAccount).where(LineBotAccount.line_bot_id == body.line_bot_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このBot IDは既に登録されています")

    bot = LineBotAccount(
        line_bot_id=body.line_bot_id,
        memo=body.memo,
        webhook_url=body.webhook_url,
        is_active=body.is_active,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    return bot


@router.patch("/{bot_id}", response_model=LineBotAccountResponse)
async def update_line_bot(
    bot_id: int,
    body: LineBotAccountUpdateRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LineBotAccount).where(LineBotAccount.id == bot_id))
    bot = result.scalar_one_or_none()
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Botが見つかりません")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bot, key, value)
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    return bot


@router.patch("/{bot_id}/toggle", response_model=LineBotAccountResponse)
async def toggle_line_bot(
    bot_id: int,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LineBotAccount).where(LineBotAccount.id == bot_id))
    bot = result.scalar_one_or_none()
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Botが見つかりません")
    bot.is_active = not bot.is_active
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    return bot
