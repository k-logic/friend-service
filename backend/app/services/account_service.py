from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.persona import Persona


async def get_display_name_map(db: AsyncSession, user_ids: list[int]) -> dict[int, str]:
    """user_id のリストから {id: display_name} の辞書を返す"""
    if not user_ids:
        return {}
    unique_ids = list(set(user_ids))
    result = await db.execute(
        select(User.id, User.display_name).where(User.id.in_(unique_ids))
    )
    return {row[0]: row[1] for row in result.all()}


async def get_user_avatar_map(db: AsyncSession, user_ids: list[int]) -> dict[int, str | None]:
    """user_id のリストから {id: avatar_url} の辞書を返す"""
    if not user_ids:
        return {}
    unique_ids = list(set(user_ids))
    result = await db.execute(
        select(User.id, User.avatar_url).where(User.id.in_(unique_ids))
    )
    return {row[0]: row[1] for row in result.all()}


async def get_persona_name_map(db: AsyncSession, persona_ids: list[int]) -> dict[int, str]:
    """persona_id のリストから {id: name} の辞書を返す"""
    if not persona_ids:
        return {}
    unique_ids = list(set(persona_ids))
    result = await db.execute(
        select(Persona.id, Persona.name).where(Persona.id.in_(unique_ids))
    )
    return {row[0]: row[1] for row in result.all()}


async def get_persona_avatar_map(db: AsyncSession, persona_ids: list[int]) -> dict[int, str | None]:
    """persona_id のリストから {id: avatar_url} の辞書を返す"""
    if not persona_ids:
        return {}
    unique_ids = list(set(persona_ids))
    result = await db.execute(
        select(Persona.id, Persona.avatar_url).where(Persona.id.in_(unique_ids))
    )
    return {row[0]: row[1] for row in result.all()}
