# Puesta en marcha (Fase 2)

Requisitos: Node 22+, Python 3.12+, Docker (para PostgreSQL con pgvector).

## 1. Base de datos
```bash
docker compose up -d db
```

## 2. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # define SECRET_KEY con un valor largo y aleatorio
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
Comprobación: http://localhost:8000/api/health

## 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Abre http://localhost:5173 y crea una cuenta. En desarrollo, Vite reenvía `/api` al backend, de modo que la cookie de sesión es del mismo origen.

En producción sirve frontend y API bajo el mismo dominio con HTTPS (`APP_ENV=production` activa `Secure` en la cookie) y define `CORS_ORIGINS` con el dominio real.

## Pruebas
```bash
cd backend && python -m pytest
cd frontend && npm test && npm run build && npm run lint
```
Las pruebas del backend usan SQLite; **no** verifican pgvector ni PostgreSQL.
