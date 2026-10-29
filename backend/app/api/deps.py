import uuid

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import Unauthorized
from app.core.security import AUTH_COOKIE, decode_access_token
from app.db.session import get_db
from app.models import User

_bearer = HTTPBearer(auto_error=False)


def get_current_user(request: Request, creds: HTTPAuthorizationCredentials | None = Depends(_bearer), db: Session = Depends(get_db)) -> User:
    # La sesión del navegador viaja en una cookie httpOnly; el encabezado Bearer queda para clientes de API.
    token = request.cookies.get(AUTH_COOKIE) or (creds.credentials if creds else None)
    user_id = decode_access_token(token) if token else None
    user = db.get(User, uuid.UUID(user_id)) if user_id else None
    if not user:
        raise Unauthorized("Sesión no válida. Inicia sesión de nuevo.")
    return user
