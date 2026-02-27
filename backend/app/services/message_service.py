from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


async def get_messages_after(db: AsyncSession, session_id: int, last_message_id: int = 0) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id, Message.id > last_message_id)
        .order_by(Message.id.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
