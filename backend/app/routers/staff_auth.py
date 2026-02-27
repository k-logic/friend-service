from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_staff
from app.models.staff_member import StaffMember
from app.schemas.auth import LoginRequest, StaffMemberResponse, TokenResponse
from app.services.auth_service import authenticate_staff, create_access_token

router = APIRouter(prefix="/api/v1/staff/auth", tags=["スタッフ認証"])


@router.post("/login", response_model=TokenResponse)
async def staff_login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    staff = await authenticate_staff(db, body.email, body.password)
    if staff is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="メールアドレスまたはパスワードが正しくありません")

    token = create_access_token(staff.id, "staff", role=staff.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=StaffMemberResponse)
async def get_staff_me(staff: StaffMember = Depends(get_current_staff)):
    return staff
