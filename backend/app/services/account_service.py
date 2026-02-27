from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.persona import Persona


async def get_display_name_map(db: AsyncSession, account_ids: list[int]) -> dict[int, str]:
    """account_id のリストから {id: display_name} の辞書を返す"""
    if not account_ids:
        return {}
    unique_ids = list(set(account_ids))
    result = await db.execute(
        select(Account.id, Account.display_name).where(Account.id.in_(unique_ids))
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
