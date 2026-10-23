from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import LoginIn, RegisterIn, TokenOut, UserOut
from services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    return register_user(db, data)

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    token = login_user(db, data.email, data.password)
    return TokenOut(access_token=token)
