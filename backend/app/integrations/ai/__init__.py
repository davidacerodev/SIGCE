from app.core.config import get_settings
from app.core.errors import AppError
from app.integrations.ai.base import AIProvider
from app.integrations.ai.mock import MockProvider


def get_ai_provider() -> AIProvider:
    provider = get_settings().ai_provider
    if provider == "mock":
        return MockProvider()
    raise AppError(f"Proveedor de IA no soportado: {provider}")
