from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_staff
from app.models.account import Account
from app.models.template import Template
from app.schemas.template import TemplateCreateRequest, TemplateResponse, TemplateUpdateRequest

router = APIRouter(prefix="/api/v1/templates", tags=["テンプレート"])


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Template).where(Template.staff_account_id == staff.id).order_by(Template.label)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateCreateRequest,
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    template = Template(staff_account_id=staff.id, label=body.label, content=body.content)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    body: TemplateUpdateRequest,
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="テンプレートが見つかりません")
    if template.staff_account_id != staff.id and staff.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    staff: Account = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="テンプレートが見つかりません")
    if template.staff_account_id != staff.id and staff.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")
    await db.delete(template)
    await db.commit()
