"""
テスト用シードデータ投入スクリプト

使い方:
  docker compose exec api python -m scripts.seed
"""

import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.user import User, UserStatus
from app.models.staff_member import StaffMember, StaffRole, StaffStatus
from app.models.persona import Persona, Gender
from app.services.auth_service import hash_password

SEED_STAFF = [
    {
        "email": "admin@example.com",
        "display_name": "管理者",
        "password": "admin1234",
        "role": StaffRole.admin,
    },
    {
        "email": "staff@example.com",
        "display_name": "スタッフA",
        "password": "staff1234",
        "role": StaffRole.staff,
    },
]

SEED_USERS = [
    {
        "email": "user@example.com",
        "display_name": "テストユーザー",
        "password": "user1234",
        "credit_balance": 1000,
    },
]

SEED_PERSONAS = [
    {
        "staff_email": "staff@example.com",
        "name": "さくら",
        "gender": Gender.female,
        "age": 24,
        "bio": "カフェ巡りとお菓子作りが趣味です。気軽にお話ししましょう！",
        "registered_at": date(2026, 1, 15),
    },
    {
        "staff_email": "staff@example.com",
        "name": "ゆうと",
        "gender": Gender.male,
        "age": 27,
        "bio": "映画と音楽が好きです。おすすめがあったら教えてください。",
        "registered_at": date(2026, 2, 1),
    },
]


async def seed(db: AsyncSession) -> None:
    # --- スタッフ ---
    created_staff: dict[str, StaffMember] = {}
    for data in SEED_STAFF:
        result = await db.execute(select(StaffMember).where(StaffMember.email == data["email"]))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  スキップ (既存): {data['email']} (id={existing.id})")
            created_staff[data["email"]] = existing
            continue

        staff = StaffMember(
            email=data["email"],
            display_name=data["display_name"],
            hashed_password=hash_password(data["password"]),
            role=data["role"],
            status=StaffStatus.active,
        )
        db.add(staff)
        await db.flush()
        created_staff[data["email"]] = staff
        print(f"  作成: {data['email']} (id={staff.id}, role={data['role'].value})")

    # --- ユーザー ---
    for data in SEED_USERS:
        result = await db.execute(select(User).where(User.email == data["email"]))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  スキップ (既存): {data['email']} (id={existing.id})")
            continue

        user = User(
            email=data["email"],
            display_name=data["display_name"],
            hashed_password=hash_password(data["password"]),
            status=UserStatus.active,
            credit_balance=data.get("credit_balance", 0),
        )
        db.add(user)
        await db.flush()
        print(f"  作成: {data['email']} (id={user.id})")

    # --- ペルソナ ---
    for data in SEED_PERSONAS:
        staff = created_staff.get(data["staff_email"])
        if not staff:
            print(f"  スキップ (スタッフ不在): ペルソナ {data['name']}")
            continue

        result = await db.execute(
            select(Persona).where(
                Persona.staff_id == staff.id,
                Persona.name == data["name"],
            )
        )
        if result.scalar_one_or_none():
            print(f"  スキップ (既存): ペルソナ {data['name']}")
            continue

        persona = Persona(
            staff_id=staff.id,
            name=data["name"],
            gender=data.get("gender"),
            age=data.get("age"),
            bio=data.get("bio"),
            registered_at=data.get("registered_at"),
            is_active=True,
        )
        db.add(persona)
        await db.flush()
        print(f"  作成: ペルソナ {data['name']} (id={persona.id})")

    await db.commit()


async def main() -> None:
    print("シードデータ投入開始...")
    async with async_session() as db:
        await seed(db)
    print("完了!")
    print()
    print("ログイン情報:")
    print("  [スタッフ]")
    for data in SEED_STAFF:
        print(f"    {data['role'].value:6s} | {data['email']} / {data['password']}")
    print("  [ユーザー]")
    for data in SEED_USERS:
        print(f"    user   | {data['email']} / {data['password']}")


if __name__ == "__main__":
    asyncio.run(main())
