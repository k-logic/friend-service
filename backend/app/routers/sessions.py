from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account
from app.models.account import Account
from app.models.persona import Persona
from app.models.session import Session, SessionStatus
from app.schemas.session import SessionCreateRequest, SessionResponse
from app.services.account_service import get_display_name_map, get_persona_name_map

router = APIRouter(prefix="/api/v1/sessions", tags=["セッション"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreateRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    # ペルソナ存在確認
    result = await db.execute(select(Persona).where(Persona.id == body.persona_id, Persona.is_active == True))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ペルソナが見つかりません")

    # 同じユーザー×ペルソナの既存アクティブセッションがあればそれを返す
    existing = await db.execute(
        select(Session).where(
            Session.user_account_id == account.id,
            Session.persona_id == body.persona_id,
            Session.status == SessionStatus.active,
        ).order_by(Session.updated_at.desc())
    )
    existing_session = existing.scalars().first()
    if existing_session:
        return existing_session

    session = Session(user_account_id=account.id, persona_id=body.persona_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    session_status: str | None = Query(None, alias="status"),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    if account.role.value in ("staff", "admin"):
        # スタッフ/管理者: 自分が担当するペルソナのセッションを返す
        my_persona_ids = await db.execute(
            select(Persona.id).where(Persona.staff_account_id == account.id)
        )
        persona_ids = [row[0] for row in my_persona_ids.all()]
        if account.role.value == "admin":
            # 管理者は全セッション
            stmt = select(Session)
        elif persona_ids:
            stmt = select(Session).where(Session.persona_id.in_(persona_ids))
        else:
            return []
    else:
        # 一般ユーザー: 自分のセッションのみ
        stmt = select(Session).where(Session.user_account_id == account.id)

    if session_status:
        stmt = stmt.where(Session.status == session_status)
    stmt = stmt.order_by(Session.updated_at.desc())
    result = await db.execute(stmt)
    sessions = list(result.scalars().all())
    name_map = await get_display_name_map(db, [s.user_account_id for s in sessions])
    persona_map = await get_persona_name_map(db, [s.persona_id for s in sessions])
    return [
        SessionResponse.model_validate(s, from_attributes=True).model_copy(
            update={
                "user_display_name": name_map.get(s.user_account_id),
                "persona_name": persona_map.get(s.persona_id),
            }
        )
        for s in sessions
    ]


@router.patch("/{session_id}/close", response_model=SessionResponse)
async def close_session(
    session_id: int,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="セッションが見つかりません")
    if session.user_account_id != account.id and account.role.value not in ("staff", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    session.status = SessionStatus.closed
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
