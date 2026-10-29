# API (prefijo `/api`)

Todas las rutas salvo `/health`, `/auth/register` y `/auth/login` requieren sesión. El navegador la mantiene con una
**cookie `access_token` httpOnly** (`SameSite=Lax`, `Path=/api`, `Secure` fuera de desarrollo) que el servidor establece en `/auth/login`
y elimina en `/auth/logout`; el token nunca es accesible desde JavaScript. Para clientes de API también se acepta `Authorization: Bearer <token>`.
Las escrituras (POST, PATCH, DELETE) con un encabezado `Origin` ajeno a `CORS_ORIGINS` se rechazan con 403 (defensa CSRF adicional).
Errores: `{"error": {"code": "...", "message": "..."}}` (401 sesión, 404 no encontrado o ajeno, 409 duplicado, 422 validación).

| Método y ruta | Descripción |
|---|---|
| `GET /health` | Estado del servidor y la base de datos |
| `POST /auth/register` · `POST /auth/login` · `POST /auth/logout` · `GET /auth/me` | Cuenta y sesión (login devuelve el usuario y fija la cookie) |
| `GET/POST /notebooks` · `GET/PATCH/DELETE /notebooks/{id}` | Cuadernos (`limit`, `offset` en el listado) |
| `GET /notebooks/{id}/sources` · `GET/DELETE .../sources/{sid}` | Fuentes y su estado (`pending`, `processing`, `ready`, `failed`) |
| `POST /notebooks/{id}/sources/text` | Fuente de texto pegado |
| `POST /notebooks/{id}/sources/upload` | Archivo PDF, TXT o MD (multipart, campo `file`) |
| `GET /notebooks/{id}/messages` · `POST /notebooks/{id}/chat` | Historial y consulta sobre fuentes (`source_ids` opcional) |
| `GET/POST /notebooks/{id}/artifacts` · `GET/DELETE .../artifacts/{aid}` | Recursos de Studio |

## Estado real frente a demostración

- **Real:** autenticación, propiedad de los datos, carga y validación de archivos, extracción de texto (PDF/TXT/MD), fragmentación, persistencia, historial.
- **Recuperación:** por coincidencia de palabras, no semántica (no hay embeddings todavía).
- **Demostración (`AI_PROVIDER=mock`):** el chat devuelve fragmentos citados y los recursos de Studio devuelven extractos, ambos con aviso explícito (`demo: true`). No hay modelo de IA conectado; se añade implementando `AIProvider` en `app/integrations/ai/`.
- **Pendiente:** fuentes por URL, límites de solicitudes y tiempos de espera del proveedor de IA, cola de tareas externa.
