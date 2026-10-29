import os

import pytest

from app.core.config import get_settings
from app.integrations.storage import get_storage
from app.integrations.storage.local import LocalFileStorage
from app.services.document_service import chunk_text


def _upload(client, auth, nb, name, data, ctype="text/plain"):
    return client.post(f"/api/notebooks/{nb}/sources/upload", files={"file": (name, data, ctype)}, headers=auth)


def _pdf(text: str) -> bytes:
    """PDF mínimo válido (con tabla xref) para pruebas."""
    stream = f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET"
    objs = [
        "<</Type/Catalog/Pages 2 0 R>>",
        "<</Type/Pages/Kids[3 0 R]/Count 1>>",
        "<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
        f"<</Length {len(stream)}>>\nstream\n{stream}\nendstream",
        "<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += f"trailer\n<</Size {len(objs) + 1}/Root 1 0 R>>\nstartxref\n{xref}\n%%EOF".encode()
    return out


def test_upload_text_is_processed_into_chunks(client, auth, notebook_id):
    r = _upload(client, auth, notebook_id, "notas.md", "# Célula\n\nLa mitocondria produce energía.".encode())
    assert r.status_code == 201
    src = client.get(f"/api/notebooks/{notebook_id}/sources/{r.json()['id']}", headers=auth).json()
    assert src["status"] == "ready" and src["name"] == "notas.md"
    assert client.get(f"/api/notebooks/{notebook_id}", headers=auth).json()["source_count"] == 1


def test_upload_pdf_extracts_text(client, auth, notebook_id):
    r = _upload(client, auth, notebook_id, "doc.pdf", _pdf("Hola mundo PDF"), "application/pdf")
    assert r.status_code == 201
    src = client.get(f"/api/notebooks/{notebook_id}/sources/{r.json()['id']}", headers=auth).json()
    assert src["status"] == "ready", src
    chat = client.post(f"/api/notebooks/{notebook_id}/chat", json={"message": "mundo"}, headers=auth)
    assert chat.status_code == 200 and "Hola mundo PDF" in chat.json()["assistant_message"]["content"]


def test_upload_validation(client, auth, notebook_id, monkeypatch):
    assert _upload(client, auth, notebook_id, "x.exe", b"MZ").status_code == 422
    assert _upload(client, auth, notebook_id, "falso.pdf", b"no soy pdf").status_code == 422
    assert _upload(client, auth, notebook_id, "bin.txt", b"abc\x00def").status_code == 422
    assert _upload(client, auth, notebook_id, "latin.txt", "ñ".encode("latin-1")).status_code == 422
    assert _upload(client, auth, notebook_id, "vacio.txt", b"").status_code == 422
    monkeypatch.setattr(get_settings(), "max_upload_mb", 1)
    assert _upload(client, auth, notebook_id, "grande.txt", b"a" * (1024 * 1024 + 1)).status_code == 422


def test_duplicate_source_rejected_but_allowed_in_other_notebook(client, auth, notebook_id):
    assert _upload(client, auth, notebook_id, "a.txt", b"mismo contenido").status_code == 201
    assert _upload(client, auth, notebook_id, "b.txt", b"mismo contenido").status_code == 409
    other = client.post("/api/notebooks", json={"title": "Otro"}, headers=auth).json()["id"]
    assert _upload(client, auth, other, "a.txt", b"mismo contenido").status_code == 201


def test_path_traversal_filename_is_neutralised(client, auth, notebook_id):
    r = _upload(client, auth, notebook_id, "../../etc/passwd.txt", b"contenido")
    assert r.status_code == 201 and r.json()["name"] == "passwd.txt"
    storage = get_storage()
    assert all(p.parent == storage.base for p in storage.base.iterdir())


def test_empty_pdf_text_marks_source_failed(client, auth, notebook_id):
    r = _upload(client, auth, notebook_id, "vacio.pdf", _pdf(""), "application/pdf")
    src = client.get(f"/api/notebooks/{notebook_id}/sources/{r.json()['id']}", headers=auth).json()
    assert src["status"] == "failed" and src["error_message"]


def test_delete_source_and_notebook_remove_files(client, auth, notebook_id):
    storage = get_storage()
    before = len(os.listdir(storage.base))
    sid = _upload(client, auth, notebook_id, "a.txt", b"uno").json()["id"]
    _upload(client, auth, notebook_id, "b.txt", b"dos")
    assert len(os.listdir(storage.base)) == before + 2
    assert client.delete(f"/api/notebooks/{notebook_id}/sources/{sid}", headers=auth).status_code == 204
    assert len(os.listdir(storage.base)) == before + 1
    client.delete(f"/api/notebooks/{notebook_id}", headers=auth)
    assert len(os.listdir(storage.base)) == before


def test_text_source_endpoint(client, auth, notebook_id):
    r = client.post(f"/api/notebooks/{notebook_id}/sources/text", json={"name": "Pegado", "content": "Texto pegado"}, headers=auth)
    assert r.status_code == 201 and r.json()["type"] == "text"


def test_chunk_text_respects_size_and_keeps_content():
    text = "\n\n".join(["párrafo " * 40] * 6) + "\n\n" + "x" * 2500
    chunks = chunk_text(text, size=1000)
    assert all(len(c) <= 1000 for c in chunks)
    assert "".join(c.replace("\n", "").replace(" ", "") for c in chunks) == text.replace("\n", "").replace(" ", "")
    assert chunk_text("   \n\n  ") == []


def test_storage_rejects_unsafe_keys(tmp_path):
    storage = LocalFileStorage(str(tmp_path))
    for key in ("../x.txt", "abc.txt", "/etc/passwd", "a" * 32 + ".exe"):
        with pytest.raises(ValueError):
            storage.save(key, b"x")
