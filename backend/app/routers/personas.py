from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account, get_current_admin, get_current_staff
from app.models.account import Account
from app.models.persona import Persona
from app.schemas.persona import PersonaCreateRequest, PersonaResponse, PersonaUpdateRequest

router = APIRouter(prefix="/api/v1/personas", tags=["ペルソナ"])


@router.get("", response_model=list[PersonaResponse])
async def list_personas(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Persona).where(Persona.is_active == True).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = result.scalar_one_or_none()
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ペルソナが見つかりません")
    return persona


@router.post("", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    body: PersonaCreateRequest,
    admin: Account = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    persona = Persona(
        staff_account_id=admin.id,
        name=body.name,
        gender=body.gender,
        age=body.age,
        avatar_url=body.avatar_url,
        bio=body.bio,
        attributes=body.attributes,
    )
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.patch("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    body: PersonaUpdateRequest,
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = result.scalar_one_or_none()
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ペルソナが見つかりません")
    if persona.staff_account_id != staff.id and staff.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)

    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.get("/staff/mine", response_model=list[PersonaResponse])
async def list_my_personas(
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Persona).where(Persona.staff_account_id == staff.id).order_by(Persona.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
