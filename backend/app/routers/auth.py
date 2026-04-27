from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserRead, UserCreate, UserUpdate
from app.security import verify_password, create_access_token, hash_password
from app.deps import get_current_user, require_admin
router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return Token(access_token=create_access_token(user.username))
@router.get("/me", response_model=UserRead)
def me(user = Depends(get_current_user)): return user

@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), user=Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("/users", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    u = User(
        username=payload.username.strip(),
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), user=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = payload.model_dump(exclude_none=True)
    if "password" in data:
        u.password_hash = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(u, k, v)
    db.commit(); db.refresh(u)
    return u

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(u); db.commit()
    return {"ok": True}
