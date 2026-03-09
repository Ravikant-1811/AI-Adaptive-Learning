# API Spec (Core)

## Health
- `GET /` -> API metadata
- `GET /api/health` -> liveness
- `GET /api/ready` -> DB readiness

## Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/login-admin`

## Learning Style
- `GET /api/style/mine`
- `POST /api/style/set`
- `POST /api/style/test`

## Chat
- `POST /api/chat/`
- `GET /api/chat/history`
- `DELETE /api/chat/history`
- `POST /api/chat/suggestions`
- `POST /api/chat/feedback`

## Practice
- `GET /api/practice/tasks`
- `POST /api/practice/run`
- `POST /api/practice/submit`

## Downloads
- `POST /api/downloads/`
- `GET /api/downloads/list`
- `GET /api/downloads/file/<download_id>`

## Admin
- `GET /api/admin/overview`
- `GET /api/admin/users`
- `GET /api/admin/chats`
- `GET /api/admin/downloads`
