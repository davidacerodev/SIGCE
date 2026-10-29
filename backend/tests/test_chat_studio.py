def _add(client, auth, nb, name, content):
    r = client.post(f"/api/notebooks/{nb}/sources/text", json={"name": name, "content": content}, headers=auth)
    assert r.status_code == 201
    return r.json()["id"]


def test_chat_requires_sources(client, auth, notebook_id):
    r = client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": "hola"}, headers=auth)
    assert r.status_code == 422
    assert client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": ""}, headers=auth).status_code == 422


def test_chat_returns_cited_fragments_and_keeps_history(client, auth, notebook_id):
    sid = _add(client, auth, notebook_id, "Biología", "La mitocondria produce energía para la célula.\n\nLos ribosomas fabrican proteínas.")
    r = client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": "¿Qué hace la mitocondria?"}, headers=auth)
    assert r.status_code == 200
    reply = r.json()["assistant_message"]
    assert "Demostración" in reply["content"] and "mitocondria" in reply["content"]
    assert reply["citations"][0]["source_id"] == sid
    history = client.get(f"/api/notebooks/{notebook_id}/messages", headers=auth).json()
    assert [m["role"] for m in history] == ["user", "assistant"]


def test_chat_without_matches_says_so_and_respects_selection(client, auth, notebook_id):
    a = _add(client, auth, notebook_id, "A", "Los ribosomas fabrican proteínas.")
    b = _add(client, auth, notebook_id, "B", "La mitocondria produce energía.")
    r = client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": "mitocondria", "source_ids": [a]}, headers=auth)
    assert r.json()["assistant_message"]["citations"] == []
    r = client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": "mitocondria", "source_ids": [b]}, headers=auth)
    assert r.json()["assistant_message"]["citations"][0]["source_id"] == b


def test_studio_generates_labeled_demo_artifact(client, auth, notebook_id):
    assert client.post(f"/api/notebooks/{notebook_id}/artifacts", json={"type": "summary"}, headers=auth).status_code == 422
    sid = _add(client, auth, notebook_id, "Notas", "Contenido de estudio.")
    r = client.post(f"/api/notebooks/{notebook_id}/artifacts", json={"type": "summary"}, headers=auth)
    assert r.status_code == 201
    art = r.json()
    assert art["status"] == "ready" and art["content"]["demo"] is True
    assert client.get(f"/api/notebooks/{notebook_id}/artifacts/{art['id']}", headers=auth).status_code == 200
    assert len(client.get(f"/api/notebooks/{notebook_id}/artifacts", headers=auth).json()) == 1
    assert client.post(f"/api/notebooks/{notebook_id}/artifacts", json={"type": "nope"}, headers=auth).status_code == 422
    assert client.delete(f"/api/notebooks/{notebook_id}/artifacts/{art['id']}", headers=auth).status_code == 204
    assert sid
