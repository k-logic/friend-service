from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.like import Like
from app.schemas.like import LikeRequest, LikeResponse

router = APIRouter(prefix="/api/v1/likes", tags=["いいね"])


@router.post("", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def send_like(
    body: LikeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Like).where(Like.user_id == user.id, Like.persona_id == body.persona_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="既にいいね済みです")

    like = Like(user_id=user.id, persona_id=body.persona_id)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_like(
    persona_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(Like).where(Like.user_id == user.id, Like.persona_id == persona_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="いいねが見つかりません")
    await db.commit()


@router.get("", response_model=list[LikeResponse])
async def list_likes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Like).where(Like.user_id == user.id).order_by(Like.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
