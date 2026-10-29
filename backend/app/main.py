from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, chat, health, notebooks, sources, studio
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    app = FastAPI(title="NotebookLM Clone API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def reject_cross_origin_writes(request, call_next):
        # Defensa CSRF adicional a SameSite=Lax: las escrituras con Origin ajeno se rechazan.
        origin = request.headers.get("origin")
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and origin:
            own = f"{request.url.scheme}://{request.url.netloc}"
            if origin != own and origin not in settings.cors_origin_list:
                return JSONResponse(
                    status_code=403,
                    content={"error": {"code": "forbidden_origin", "message": "Origen no permitido."}},
                )
        return await call_next(request)

    register_error_handlers(app)
    for router in (health.router, auth.router, notebooks.router, sources.router, chat.router, studio.router):
        app.include_router(router, prefix="/api")
    return app


app = create_app()
