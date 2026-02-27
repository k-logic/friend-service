from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account, get_current_admin
from app.models.account import Account
from app.models.inquiry import Inquiry, InquiryStatus
from app.schemas.admin import InquiryCreateRequest, InquiryReplyRequest, InquiryResponse
from app.services.account_service import get_display_name_map

router = APIRouter(prefix="/api/v1/inquiries", tags=["問い合わせ"])


# --- ユーザー側 ---
@router.post("", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    body: InquiryCreateRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    inquiry = Inquiry(account_id=account.id, subject=body.subject, body=body.body)
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    return inquiry


@router.get("/mine", response_model=list[InquiryResponse])
async def list_my_inquiries(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Inquiry).where(Inquiry.account_id == account.id).order_by(Inquiry.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


# --- 管理者側 ---
@router.get("", response_model=list[InquiryResponse])
async def list_all_inquiries(
    inquiry_status: str | None = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Inquiry)
    if inquiry_status:
        stmt = stmt.where(Inquiry.status == inquiry_status)
    stmt = stmt.order_by(Inquiry.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    inquiries = list(result.scalars().all())
    name_map = await get_display_name_map(db, [inq.account_id for inq in inquiries])
    return [
        InquiryResponse.model_validate(inq, from_attributes=True).model_copy(
            update={"account_display_name": name_map.get(inq.account_id)}
        )
        for inq in inquiries
    ]


@router.patch("/{inquiry_id}/reply", response_model=InquiryResponse)
async def reply_inquiry(
    inquiry_id: int,
    body: InquiryReplyRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id))
    inquiry = result.scalar_one_or_none()
    if inquiry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="問い合わせが見つかりません")
    inquiry.admin_reply = body.admin_reply
    inquiry.status = InquiryStatus.replied
    inquiry.replied_at = datetime.now(timezone.utc)
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    name_map = await get_display_name_map(db, [inquiry.account_id])
    return InquiryResponse.model_validate(inquiry, from_attributes=True).model_copy(
        update={"account_display_name": name_map.get(inquiry.account_id)}
    )


@router.delete("/{inquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inquiry(
    inquiry_id: int,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id))
    inquiry = result.scalar_one_or_none()
    if inquiry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="問い合わせが見つかりません")
    await db.delete(inquiry)
    await db.commit()
