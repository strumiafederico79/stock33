from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserRead
from app.security import verify_password, create_access_token
from app.deps import get_current_user
router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return Token(access_token=create_access_token(user.username))
@router.get("/me", response_model=UserRead)
def me(user = Depends(get_current_user)): return user
