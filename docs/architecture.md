# Adaptive AI Learning Platform - Architecture

## Current Modular Backend
- Entry point: `backend/run.py`
- App factory: `backend/app/__init__.py`
- Config module: `backend/app/config.py`
- DB/JWT extensions: `backend/app/extensions.py`
- Models: `backend/app/models.py`
- Routes: `backend/app/routes/*.py`
- Services: `backend/app/services/*.py`

## Request Flow
1. Frontend (Vite + React) sends API request to Flask backend (`/api/*`).
2. Route validates payload and auth token.
3. Service layer executes adaptive learning logic (style/chat/practice/download).
4. SQLAlchemy persists records in PostgreSQL/SQLite.
5. API response returns learner-specific result.

## Deployment Shape
- Frontend: Vercel static build (`frontend/vercel.json`)
- Backend: Render web service (`render.yaml`)
- Database: Neon PostgreSQL (`DATABASE_URL`)

## Admin/User Separation
- User auth endpoints: `auth` routes.
- Admin auth + dashboard endpoints: `admin` routes.
- Admin access controlled via `ADMIN_EMAILS` and JWT role checks.
