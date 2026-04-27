from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password
from app.routers import auth, core
settings=get_settings()
app=FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)
Path("/data/contracts").mkdir(parents=True, exist_ok=True); Path("/data/backups").mkdir(parents=True, exist_ok=True)
app.mount("/static/contracts", StaticFiles(directory="/data/contracts"), name="contracts")
def seed_admin():
    db: Session = SessionLocal()
    try:
        if not db.query(User).filter(User.username==settings.default_admin_username).first():
            db.add(User(username=settings.default_admin_username, full_name=settings.default_admin_full_name, password_hash=hash_password(settings.default_admin_password), role="admin", is_active=True)); db.commit()
    finally: db.close()
seed_admin()
@app.get("/health")
def health(): return {"ok": True, "app": settings.app_name}
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(core.router, prefix=settings.api_prefix)
