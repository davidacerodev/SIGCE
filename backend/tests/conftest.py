import os

# Las pruebas usan SQLite en memoria de archivo temporal; debe fijarse antes de importar la app.
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="uploads-test-")

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, get_db
from app.main import app


@event.listens_for(engine, "connect")
def _sqlite_fk_on(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


@pytest.fixture()
def db():
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db):
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _register(client, email):
    body = {"email": email, "password": "password123", "display_name": email.split("@")[0]}
    assert client.post("/api/auth/register", json=body).status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login.cookies.get("access_token")
    client.cookies.clear()  # cada usuario se identifica con su propio encabezado en las pruebas
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth(client):
    return _register(client, "ana@example.com")


@pytest.fixture()
def other_auth(client):
    return _register(client, "luis@example.com")


@pytest.fixture()
def notebook_id(client, auth):
    return client.post("/api/notebooks", json={"title": "Biología"}, headers=auth).json()["id"]
