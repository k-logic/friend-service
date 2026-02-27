import time
from pathlib import Path
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

UPLOAD_DIR = Path("/app/uploads/personas")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024
from app.dependencies import get_current_account, get_current_admin, get_current_staff
from app.models.user import User
from app.models.staff_member import StaffMember, StaffRole
from app.models.persona import Persona
from app.schemas.persona import PersonaCreateRequest, PersonaResponse, PersonaUpdateRequest

router = APIRouter(prefix="/api/v1/personas", tags=["ペルソナ"])


@router.get("", response_model=list[PersonaResponse])
async def list_personas(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    account: Union[User, StaffMember] = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Persona).where(Persona.is_active == True).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    account: Union[User, StaffMember] = Depends(get_current_account),
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
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    persona = Persona(
        staff_id=admin.id,
        name=body.name,
        gender=body.gender,
        age=body.age,
        avatar_url=body.avatar_url,
        bio=body.bio,
        attributes=body.attributes,
        registered_at=body.registered_at,
    )
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.patch("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    body: PersonaUpdateRequest,
    staff: StaffMember = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = result.scalar_one_or_none()
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ペルソナが見つかりません")
    if persona.staff_id != staff.id and staff.role != StaffRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)

    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.post("/{persona_id}/avatar", response_model=PersonaResponse)
async def upload_persona_avatar(
    persona_id: int,
    file: UploadFile,
    staff: StaffMember = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="JPEG, PNG, WebP のみアップロード可能です")

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズは5MB以下にしてください")

    result = await db.execute(select(Persona).where(Persona.id == persona_id))
    persona = result.scalar_one_or_none()
    if persona is None:
        raise HTTPException(status_code=404, detail="ペルソナが見つかりません")
    if persona.staff_id != staff.id and staff.role != StaffRole.admin:
        raise HTTPException(status_code=403, detail="権限がありません")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    filename = f"persona_{persona_id}_{int(time.time())}.{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if persona.avatar_url:
        old_path = Path("/app") / persona.avatar_url.lstrip("/")
        if old_path.exists():
            old_path.unlink()

    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(data)

    persona.avatar_url = f"/uploads/personas/{filename}"
    await db.commit()
    await db.refresh(persona)
    return persona


@router.get("/staff/mine", response_model=list[PersonaResponse])
async def list_my_personas(
    staff: StaffMember = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Persona).where(Persona.staff_id == staff.id).order_by(Persona.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
