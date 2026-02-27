from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account, get_current_admin
from app.models.account import Account
from app.models.age_verification import AgeVerification, VerificationStatus
from app.schemas.admin import AgeVerificationResponse, AgeVerificationReviewRequest
from app.services.account_service import get_display_name_map

router = APIRouter(prefix="/api/v1/age-verification", tags=["年齢認証"])


# --- ユーザー側 ---
@router.post("/submit", response_model=AgeVerificationResponse, status_code=status.HTTP_201_CREATED)
async def submit_verification(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(AgeVerification).where(
            AgeVerification.account_id == account.id,
            AgeVerification.status == VerificationStatus.pending,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="審査中の申請が既にあります")

    verification = AgeVerification(account_id=account.id)
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    return verification


# --- 管理者側 ---
@router.get("", response_model=list[AgeVerificationResponse])
async def list_verifications(
    verification_status: str | None = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AgeVerification)
    if verification_status:
        stmt = stmt.where(AgeVerification.status == verification_status)
    stmt = stmt.order_by(AgeVerification.submitted_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    name_map = await get_display_name_map(db, [v.account_id for v in items])
    return [
        AgeVerificationResponse.model_validate(v, from_attributes=True).model_copy(
            update={"account_display_name": name_map.get(v.account_id)}
        )
        for v in items
    ]


@router.patch("/{verification_id}/review", response_model=AgeVerificationResponse)
async def review_verification(
    verification_id: int,
    body: AgeVerificationReviewRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AgeVerification).where(AgeVerification.id == verification_id))
    verification = result.scalar_one_or_none()
    if verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申請が見つかりません")

    verification.status = VerificationStatus(body.status)
    verification.reviewed_at = datetime.now(timezone.utc)
    verification.reviewer_id = admin.id
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    name_map = await get_display_name_map(db, [verification.account_id])
    return AgeVerificationResponse.model_validate(verification, from_attributes=True).model_copy(
        update={"account_display_name": name_map.get(verification.account_id)}
    )
