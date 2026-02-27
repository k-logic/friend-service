from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.account import Account
from app.models.paid_content import PaidContent
from app.schemas.admin import PaidContentCreateRequest, PaidContentResponse

router = APIRouter(prefix="/api/v1/admin/paid-contents", tags=["管理: 有料情報"])


@router.get("", response_model=list[PaidContentResponse])
async def list_paid_contents(
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PaidContent).order_by(PaidContent.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=PaidContentResponse, status_code=status.HTTP_201_CREATED)
async def create_paid_content(
    body: PaidContentCreateRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    content = PaidContent(
        title=body.title, description=body.description, price=body.price, is_active=body.is_active
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content


@router.patch("/{content_id}/toggle", response_model=PaidContentResponse)
async def toggle_paid_content(
    content_id: int,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PaidContent).where(PaidContent.id == content_id))
    content = result.scalar_one_or_none()
    if content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="有料情報が見つかりません")
    content.is_active = not content.is_active
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content
