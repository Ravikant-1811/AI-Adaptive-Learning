# AI-Powered Adaptive Learning Platform

Adaptive AI learning platform with personalized delivery by learning style (Visual, Auditory, Kinesthetic), chatbot + synced practice lab, downloads, and progress tracking.

## Core Features
- Authentication: register/login/logout + password reset
- Learning style: direct selection or AI-generated MCQ assessment
- Adaptive dashboard with metrics
- Style-aware AI chatbot (visual/auditory/kinesthetic outputs)
- Chat-to-practice synchronization
- Java virtual lab with run + submit + tracking
- Download generation/history

## Tech Stack
- Frontend: React + Vite + Bootstrap
- Backend: Flask + SQLAlchemy + JWT
- AI: OpenAI API (text + optional TTS)
- Practice execution: Judge0 (optional) + local Java/simulation fallback
- Production DB: PostgreSQL

## Local Development

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 run.py
```
Backend: `http://127.0.0.1:5001`

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Frontend: `http://127.0.0.1:5173` (or next available port)

## Production Deployment (Docker)

### 1. Configure secrets
Edit `docker-compose.prod.yml` and change at minimum:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `POSTGRES_PASSWORD`

Also export optional AI variables before run:
```bash
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="gpt-4o-mini"
```

### 2. Build and run
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 3. Access
- Frontend (Nginx): `http://localhost:8080`
- Backend API: `http://localhost:5001`
- Health: `http://localhost:5001/api/health`
- Readiness: `http://localhost:5001/api/ready`

### 4. Stop
```bash
docker compose -f docker-compose.prod.yml down
```

## Production Hardening Included
- Gunicorn backend server (`backend/Dockerfile`)
- PostgreSQL-backed compose stack
- Nginx frontend serving built React app (`frontend/Dockerfile`, `frontend/nginx.conf`)
- API readiness endpoint (`/api/ready`) with DB check
- SQLite lock mitigation for local mode (WAL + timeout)
- Environment-based CORS and secret validation in production

## Important Files
- Backend app config: `backend/app/__init__.py`
- Backend WSGI entry: `backend/wsgi.py`
- Backend image: `backend/Dockerfile`
- Frontend image: `frontend/Dockerfile`
- Frontend Nginx config: `frontend/nginx.conf`
- Production compose: `docker-compose.prod.yml`

## API Summary
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/auth/forgot-password`, `/api/auth/reset-password`
- Style: `/api/style/questions`, `/api/style/generate-questions`, `/api/style/select`, `/api/style/submit-test`, `/api/style/mine`
- Chat: `/api/chat/`, `/api/chat/history`
- Practice: `/api/practice/topics`, `/api/practice/tasks`, `/api/practice/run`, `/api/practice/submit`, `/api/practice/mine`
- Downloads: `/api/downloads/`, `/api/downloads/mine`, `/api/downloads/file/<download_id>`
