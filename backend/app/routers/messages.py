from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account
from app.models.user import User
from app.models.staff_member import StaffMember
from app.models.message import Message, SenderType
from app.models.session import Session, SessionStatus
from app.schemas.message import MessagePollResponse, MessageResponse, MessageSendRequest
from app.services.account_service import get_display_name_map
from app.services.credit_service import deduct_credits
from app.services.message_service import get_messages_after

router = APIRouter(prefix="/api/v1/messages", tags=["メッセージ"])

CREDIT_COST_PER_MESSAGE = 1


@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: MessageSendRequest,
    account: Union[User, StaffMember] = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    # セッション存在確認 + 権限チェック
    result = await db.execute(select(Session).where(Session.id == body.session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="セッションが見つかりません")
    if isinstance(account, User) and session.user_id != account.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")
    if session.status != SessionStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="このセッションは終了しています")

    # ユーザーの場合はクレジット減算
    if isinstance(account, User):
        await deduct_credits(db, account, CREDIT_COST_PER_MESSAGE)
        sender_type = SenderType.user
    else:
        sender_type = SenderType.persona

    message = Message(
        session_id=body.session_id,
        sender_type=sender_type,
        sender_id=account.id,
        title=body.title,
        content=body.content,
        image_url=body.image_url,
        credit_cost=CREDIT_COST_PER_MESSAGE if sender_type == SenderType.user else 0,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/poll", response_model=MessagePollResponse)
async def poll_messages(
    session_id: int = Query(...),
    last_message_id: int = Query(0),
    account: Union[User, StaffMember] = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    # セッション権限チェック
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="セッションが見つかりません")
    if isinstance(account, User) and session.user_id != account.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    messages = await get_messages_after(db, session_id, last_message_id)
    new_last_id = messages[-1].id if messages else last_message_id or None
    name_map = await get_display_name_map(db, [m.sender_id for m in messages])
    return MessagePollResponse(
        messages=[
            MessageResponse.model_validate(m).model_copy(
                update={"sender_display_name": name_map.get(m.sender_id)}
            )
            for m in messages
        ],
        last_message_id=new_last_id,
    )
