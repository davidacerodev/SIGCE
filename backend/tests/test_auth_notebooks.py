def test_register_login_me_and_errors(client, auth):
    me = client.get("/api/auth/me", headers=auth)
    assert me.status_code == 200 and me.json()["email"] == "ana@example.com"
    dup = client.post("/api/auth/register", json={"email": "ANA@example.com", "password": "password123", "display_name": "x"})
    assert dup.status_code == 409
    assert client.post("/api/auth/login", json={"email": "ana@example.com", "password": "wrong-pass"}).status_code == 401
    bad = client.post("/api/auth/register", json={"email": "bad", "password": "short", "display_name": "x"})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "validation_failed"
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_notebook_crud(client, auth):
    assert client.get("/api/notebooks", headers=auth).json() == []
    assert client.post("/api/notebooks", json={"title": ""}, headers=auth).status_code == 422
    nb = client.post("/api/notebooks", json={"title": "  Historia ", "description": "d"}, headers=auth).json()
    assert nb["title"] == "Historia" and nb["source_count"] == 0
    patched = client.patch(f"/api/notebooks/{nb['id']}", json={"title": "Historia 2"}, headers=auth).json()
    assert patched["title"] == "Historia 2" and patched["description"] == "d"
    assert len(client.get("/api/notebooks", headers=auth).json()) == 1
    assert client.delete(f"/api/notebooks/{nb['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/notebooks/{nb['id']}", headers=auth).status_code == 404


def test_notebooks_are_private_per_user(client, auth, other_auth, notebook_id):
    url = f"/api/notebooks/{notebook_id}"
    assert client.get(url, headers=other_auth).status_code == 404
    assert client.patch(url, json={"title": "x"}, headers=other_auth).status_code == 404
    assert client.delete(url, headers=other_auth).status_code == 404
    assert client.get(f"{url}/sources", headers=other_auth).status_code == 404
    assert client.post(f"{url}/chat", json={"message": "hola"}, headers=other_auth).status_code == 404
    assert client.get("/api/notebooks", headers=other_auth).json() == []
    assert client.get(url, headers=auth).status_code == 200


def test_login_sets_httponly_cookie_and_cookie_authenticates(client):
    body = {"email": "c@example.com", "password": "password123", "display_name": "C"}
    client.post("/api/auth/register", json=body)
    r = client.post("/api/auth/login", json={"email": body["email"], "password": body["password"]})
    assert r.status_code == 200 and "access_token" not in r.json()
    header = r.headers["set-cookie"].lower()
    assert "httponly" in header and "samesite=lax" in header and "path=/api" in header
    assert client.get("/api/auth/me").json()["email"] == "c@example.com"  # solo cookie, sin Bearer

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_cross_origin_writes_are_rejected(client, auth):
    bad = client.post("/api/notebooks", json={"title": "x"}, headers={**auth, "Origin": "https://evil.example"})
    assert bad.status_code == 403
    ok = client.post("/api/notebooks", json={"title": "x"}, headers={**auth, "Origin": "http://localhost:5173"})
    assert ok.status_code == 201
