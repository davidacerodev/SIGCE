from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import AUTH_COOKIE
from app.db.session import get_db
from app.models import User
from app.schemas.api import Credentials, RegisterIn, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=UserOut)
def login(data: Credentials, response: Response, db: Session = Depends(get_db)):
    user, token = auth_service.login(db, data)
    settings = get_settings()
    response.set_cookie(
        AUTH_COOKIE, token,
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.app_env != "development",
        path="/api",
    )
    return user


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(AUTH_COOKIE, path="/api")
    response.status_code = 204
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
