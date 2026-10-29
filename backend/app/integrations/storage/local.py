import re
from pathlib import Path

_KEY = re.compile(r"^[0-9a-f]{32}\.(txt|md|pdf)$")


class LocalFileStorage:
    """Almacenamiento en disco. Las claves las genera el servidor; se rechaza cualquier otra forma."""

    def __init__(self, base_dir: str):
        self.base = Path(base_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if not _KEY.match(key):
            raise ValueError("Clave de almacenamiento inválida")
        return self.base / key

    def save(self, key: str, data: bytes) -> None:
        self._path(key).write_bytes(data)

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)
