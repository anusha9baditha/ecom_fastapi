from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas import RegisterIn
from utils.security import hash_password, verify_password, create_access_token

def register_user(db: Session, data: RegisterIn) -> User:
    email = str(data.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(name=data.name.strip(), email=email, hashed_password=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == str(email).lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return create_access_token(user.id, user.role)
