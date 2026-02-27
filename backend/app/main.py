import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth,
    messages,
    sessions,
    credits,
    personas,
    likes,
    footprints,
    notifications,
    templates,
    inquiries,
    invitations,
    admin_users,
    admin_paid_contents,
    admin_mail,
    admin_line_bot,
    admin_age_verification,
)

app = FastAPI(title="Friend API", version="0.1.0")

# CORS設定: ALLOWED_ORIGINS が設定されていれば本番モード、なければ開発モード
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# コア機能
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(sessions.router)
app.include_router(credits.router)
app.include_router(personas.router)

# サブ機能
app.include_router(likes.router)
app.include_router(footprints.router)
app.include_router(notifications.router)
app.include_router(templates.router)
app.include_router(inquiries.router)
app.include_router(invitations.router)

# 管理系
app.include_router(admin_users.router)
app.include_router(admin_paid_contents.router)
app.include_router(admin_mail.router)
app.include_router(admin_line_bot.router)
app.include_router(admin_age_verification.router)


# 静的ファイル配信（アバター画像等）
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
