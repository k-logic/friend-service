from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account, get_current_staff
from app.models.account import Account
from app.models.footprint import Footprint
from app.schemas.footprint import FootprintCreateRequest, FootprintResponse

router = APIRouter(prefix="/api/v1/footprints", tags=["足跡"])


@router.post("", response_model=FootprintResponse, status_code=status.HTTP_201_CREATED)
async def record_footprint(
    body: FootprintCreateRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    # 同じユーザー×ペルソナの既存足跡があれば日時を更新
    result = await db.execute(
        select(Footprint).where(
            Footprint.visitor_account_id == account.id,
            Footprint.persona_id == body.persona_id,
        )
    )
    existing = result.scalars().first()
    if existing:
        existing.created_at = datetime.now(timezone.utc)
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return existing

    footprint = Footprint(visitor_account_id=account.id, persona_id=body.persona_id)
    db.add(footprint)
    await db.commit()
    await db.refresh(footprint)
    return footprint


@router.get("/mine", response_model=list[FootprintResponse])
async def list_my_footprints(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Footprint)
        .where(Footprint.visitor_account_id == account.id)
        .order_by(Footprint.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/persona/{persona_id}", response_model=list[FootprintResponse])
async def list_persona_footprints(
    persona_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Footprint)
        .where(Footprint.persona_id == persona_id)
        .order_by(Footprint.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
