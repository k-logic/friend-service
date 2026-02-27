import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.models.staff_member import StaffMember
from app.models.invitation import InvitationToken
from app.schemas.auth import TokenResponse
from app.schemas.invitation import (
    InvitationCreateRequest,
    InvitationRegisterRequest,
    InvitationResponse,
    InvitationVerifyResponse,
)
from app.services.auth_service import create_access_token, hash_password

router = APIRouter(prefix="/api/v1/invitations", tags=["招待"])

INVITE_BASE_URL = "http://localhost:3000/invite"
INVITE_EXPIRE_HOURS = 72


@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    body: InvitationCreateRequest,
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # 既存ユーザーチェック
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    token = secrets.token_urlsafe(32)
    invitation = InvitationToken(
        token=token,
        email=body.email,
        created_by=admin.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=INVITE_EXPIRE_HOURS),
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    return {
        **{c.name: getattr(invitation, c.name) for c in invitation.__table__.columns},
        "invite_url": f"{INVITE_BASE_URL}?token={token}",
    }


@router.get("", response_model=list[InvitationResponse])
async def list_invitations(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: StaffMember = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(InvitationToken)
        .order_by(InvitationToken.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    invitations = list(result.scalars().all())
    return [
        {
            **{c.name: getattr(inv, c.name) for c in inv.__table__.columns},
            "invite_url": f"{INVITE_BASE_URL}?token={inv.token}",
        }
        for inv in invitations
    ]


@router.get("/{token}/verify", response_model=InvitationVerifyResponse)
async def verify_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    invitation = await _get_valid_invitation(db, token)
    return InvitationVerifyResponse(email=invitation.email)


@router.post("/{token}/register", response_model=TokenResponse)
async def register_by_invitation(
    token: str,
    body: InvitationRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    invitation = await _get_valid_invitation(db, token)

    # メールアドレス重複チェック
    result = await db.execute(select(User).where(User.email == invitation.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # ユーザー作成（ランダムパスワード）
    random_password = secrets.token_urlsafe(16)
    user = User(
        email=invitation.email,
        display_name=body.display_name,
        hashed_password=hash_password(random_password),
    )
    db.add(user)
    await db.flush()

    # トークンを使用済みに更新
    invitation.used_at = datetime.now(timezone.utc)
    invitation.used_by = user.id
    db.add(invitation)

    await db.commit()

    access_token = create_access_token(user.id, "user")
    return TokenResponse(access_token=access_token)


async def _get_valid_invitation(db: AsyncSession, token: str) -> InvitationToken:
    result = await db.execute(
        select(InvitationToken).where(InvitationToken.token == token)
    )
    invitation = result.scalar_one_or_none()

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="招待リンクが見つかりません"
        )
    if invitation.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="この招待リンクは既に使用されています"
        )
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="この招待リンクは有効期限切れです"
        )

    return invitation
