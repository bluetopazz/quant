from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.intelligence import router as intelligence_router
from backend.app.api.routes.journals import router as journals_router
from backend.app.api.routes.pairs import router as pairs_router
from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.db.models import User
from backend.app.db.session import SessionLocal, init_db
from backend.app.services.intelligence_service import ensure_background_refresh_started


app = FastAPI(title=settings.api_title, version=settings.api_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(intelligence_router)
app.include_router(pairs_router)
app.include_router(journals_router)


def _seed_default_user() -> None:
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.admin_username).one_or_none()
        if existing is None:
            db.add(
                User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    role="operator",
                )
            )
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    _seed_default_user()
    ensure_background_refresh_started()
