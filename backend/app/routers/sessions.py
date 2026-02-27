from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account, get_current_user
from app.models.user import User
from app.models.staff_member import StaffMember, StaffRole
from app.models.persona import Persona
from app.models.session import Session, SessionStatus
from app.models.message import Message, SenderType
from app.schemas.session import SessionCreateRequest, SessionResponse
from app.services.account_service import (
    get_display_name_map,
    get_persona_name_map,
    get_user_avatar_map,
    get_persona_avatar_map,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["セッション"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # ペルソナ存在確認
    result = await db.execute(select(Persona).where(Persona.id == body.persona_id, Persona.is_active == True))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ペルソナが見つかりません")

    # 同じユーザー×ペルソナの既存アクティブセッションがあればそれを返す
    existing = await db.execute(
        select(Session).where(
            Session.user_id == user.id,
            Session.persona_id == body.persona_id,
            Session.status == SessionStatus.active,
        ).order_by(Session.updated_at.desc())
    )
    existing_session = existing.scalars().first()
    if existing_session:
        return existing_session

    session = Session(user_id=user.id, persona_id=body.persona_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    session_status: str | None = Query(None, alias="status"),
    account: Union[User, StaffMember] = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    if isinstance(account, StaffMember):
        # スタッフ/管理者: 自分が担当するペルソナのセッションを返す
        my_persona_ids = await db.execute(
            select(Persona.id).where(Persona.staff_id == account.id)
        )
        persona_ids = [row[0] for row in my_persona_ids.all()]
        if account.role == StaffRole.admin:
            # 管理者は全セッション
            stmt = select(Session)
        elif persona_ids:
            stmt = select(Session).where(Session.persona_id.in_(persona_ids))
        else:
            return []
    else:
        # 一般ユーザー: 自分のセッションのみ
        stmt = select(Session).where(Session.user_id == account.id)

    if session_status:
        stmt = stmt.where(Session.status == session_status)
    stmt = stmt.order_by(Session.updated_at.desc())
    result = await db.execute(stmt)
    sessions = list(result.scalars().all())
    user_ids = [s.user_id for s in sessions]
    persona_ids = [s.persona_id for s in sessions]
    name_map = await get_display_name_map(db, user_ids)
    user_avatar_map = await get_user_avatar_map(db, user_ids)
    persona_map = await get_persona_name_map(db, persona_ids)
    persona_avatar_map = await get_persona_avatar_map(db, persona_ids)

    # 各セッションの最新ペルソナメッセージを取得
    session_ids = [s.id for s in sessions]
    last_msg_map: dict[int, str] = {}
    if session_ids:
        # セッションごとの最新ペルソナメッセージIDを取得
        sub = (
            select(
                Message.session_id,
                func.max(Message.id).label("max_id"),
            )
            .where(
                Message.session_id.in_(session_ids),
                Message.sender_type == SenderType.persona,
            )
            .group_by(Message.session_id)
            .subquery()
        )
        stmt_msg = select(Message).join(
            sub,
            (Message.session_id == sub.c.session_id) & (Message.id == sub.c.max_id),
        )
        msg_result = await db.execute(stmt_msg)
        for msg in msg_result.scalars().all():
            last_msg_map[msg.session_id] = msg.content

    return [
        SessionResponse.model_validate(s, from_attributes=True).model_copy(
            update={
                "user_display_name": name_map.get(s.user_id),
                "user_avatar_url": user_avatar_map.get(s.user_id),
                "persona_name": persona_map.get(s.persona_id),
                "persona_avatar_url": persona_avatar_map.get(s.persona_id),
                "last_persona_message": last_msg_map.get(s.id),
            }
        )
        for s in sessions
    ]


@router.patch("/{session_id}/close", response_model=SessionResponse)
async def close_session(
    session_id: int,
    account: Union[User, StaffMember] = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="セッションが見つかりません")
    if isinstance(account, User) and session.user_id != account.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    session.status = SessionStatus.closed
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
