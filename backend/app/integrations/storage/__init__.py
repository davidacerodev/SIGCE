from functools import lru_cache

from app.core.config import get_settings
from app.integrations.storage.base import FileStorage
from app.integrations.storage.local import LocalFileStorage


@lru_cache
def get_storage() -> FileStorage:
    return LocalFileStorage(get_settings().upload_dir)
