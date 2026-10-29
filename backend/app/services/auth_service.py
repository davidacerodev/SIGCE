from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import Conflict, Unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.api import Credentials, RegisterIn

_DUMMY_HASH = hash_password("dummy-password")


def register(db: Session, data: RegisterIn) -> User:
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise Conflict("Ya existe una cuenta con ese correo.")
    user = User(email=email, display_name=data.display_name.strip(), password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return user


def login(db: Session, data: Credentials) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    # Se verifica siempre un hash para no revelar por tiempo si el correo existe.
    ok = verify_password(data.password, user.password_hash if user else _DUMMY_HASH)
    if not user or not ok:
        raise Unauthorized("Correo o contraseña incorrectos.")
    return user, create_access_token(str(user.id))
