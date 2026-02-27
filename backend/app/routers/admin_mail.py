from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.staff_member import StaffMember
from app.models.mail_campaign import MailCampaign, CampaignType, CampaignStatus, TriggerMailSetting
from app.schemas.admin import (
    MailCampaignCreateRequest,
    MailCampaignResponse,
    TriggerMailSettingCreateRequest,
    TriggerMailSettingResponse,
)

router = APIRouter(prefix="/api/v1/admin/mail", tags=["管理: メール配信"])


@router.get("/campaigns", response_model=list[MailCampaignResponse])
async def list_campaigns(
    campaign_type: str | None = Query(None, alias="type"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(MailCampaign)
    if campaign_type:
        stmt = stmt.where(MailCampaign.type == campaign_type)
    stmt = stmt.order_by(MailCampaign.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/campaigns", response_model=MailCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    body: MailCampaignCreateRequest,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    campaign = MailCampaign(
        type=CampaignType(body.type),
        subject=body.subject,
        body=body.body,
        target_filter=body.target_filter,
        scheduled_at=body.scheduled_at,
        interval=body.interval,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.patch("/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: int,
    new_status: str = Query(..., alias="status"),
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MailCampaign).where(MailCampaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="キャンペーンが見つかりません")
    campaign.status = CampaignStatus(new_status)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return MailCampaignResponse.model_validate(campaign)


# --- トリガーメール ---
@router.get("/triggers", response_model=list[TriggerMailSettingResponse])
async def list_triggers(
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TriggerMailSetting).order_by(TriggerMailSetting.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/triggers", response_model=TriggerMailSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    body: TriggerMailSettingCreateRequest,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    trigger = TriggerMailSetting(
        trigger_event=body.trigger_event,
        mail_campaign_id=body.mail_campaign_id,
        delay_minutes=body.delay_minutes,
        is_active=body.is_active,
    )
    db.add(trigger)
    await db.commit()
    await db.refresh(trigger)
    return trigger


@router.patch("/triggers/{trigger_id}/toggle", response_model=TriggerMailSettingResponse)
async def toggle_trigger(
    trigger_id: int,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TriggerMailSetting).where(TriggerMailSetting.id == trigger_id))
    trigger = result.scalar_one_or_none()
    if trigger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="トリガー設定が見つかりません")
    trigger.is_active = not trigger.is_active
    db.add(trigger)
    await db.commit()
    await db.refresh(trigger)
    return trigger
