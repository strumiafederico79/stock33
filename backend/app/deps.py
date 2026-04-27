from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.security import decode_access_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try: username = decode_access_token(token).get("sub")
    except Exception: raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Usuario inválido")
    return user
def require_admin(user = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Solo admin")
    return user
