# Complete Setup Guide (Render + Vercel + Neon)

## 1. Backend (Render)

1. Create a new **Web Service** from this repo.
2. Use these values:
   - Environment: `Production`
   - Language: `Python 3`
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Health Check Path: `/api/health`
3. Add environment variables:
   - `APP_ENV=production`
   - `SECRET_KEY=<strong-random>`
   - `JWT_SECRET_KEY=<strong-random>`
   - `JWT_ACCESS_TOKEN_EXPIRES_SECONDS=86400`
   - `DATABASE_URL=<neon-postgres-url-with-sslmode=require>`
   - `CORS_ORIGINS=https://<your-vercel-domain>,https://<your-custom-domain>,https://www.<your-custom-domain>`
   - `ADMIN_EMAILS=admin@example.com`
   - `OPENAI_API_KEY=<your-openai-key>`
   - `OPENAI_MODEL=gpt-4o-mini`
   - `OPENAI_TTS_MODEL=gpt-4o-mini-tts`
   - `OPENAI_TTS_VOICE=alloy`
   - `ELEVENLABS_API_KEY=<your-elevenlabs-key>`
   - `ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL`
   - `ELEVENLABS_MODEL_ID=eleven_multilingual_v2`

### Important DB note
Use this format in `DATABASE_URL`:
`postgresql://.../neondb?sslmode=require`

Do not keep `&channel_binding=require`.

### Backend validation
- Health: `https://<render-app>.onrender.com/api/health`
- Ready (DB): `https://<render-app>.onrender.com/api/ready`

`/api/ready` must return `{"status":"ready"}`.

## 2. Frontend (Vercel)

1. Import repo in Vercel.
2. Set:
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
3. Add env var:
   - `VITE_API_BASE_URL=https://<render-app>.onrender.com/api`
4. Deploy.

`frontend/vercel.json` is included to fix SPA route refresh 404.

## 3. Domain setup

1. In Vercel, add `yourdomain.com` and `www.yourdomain.com`.
2. Add DNS records at domain provider as shown by Vercel.
3. Optional backend subdomain:
   - Add custom domain in Render (for example `api.yourdomain.com`)
   - Add CNAME in DNS.

## 4. Admin setup

1. Set `ADMIN_EMAILS` in Render (comma-separated admin emails).
2. Register that email once from UI or API.
3. Login via Admin Login page.

API test:
```bash
curl -X POST https://<render-app>.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin","email":"admin@example.com","password":"Admin@123"}'

curl -X POST https://<render-app>.onrender.com/api/auth/login-admin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@123"}'
```

## 5. Quick troubleshooting

- `Registration failed` in UI:
  - Verify Vercel env is exactly: `https://<render-app>.onrender.com/api`
  - Redeploy Vercel.

- `/api/ready` returns `not_ready`:
  - Fix `DATABASE_URL`.
  - Ensure Neon password/db is valid.
  - Redeploy Render.

- Route shows `404 NOT_FOUND` on refresh:
  - Ensure `frontend/vercel.json` exists and redeploy.

- Chatbot request fails:
  - Verify `OPENAI_API_KEY` in Render.
  - Check Render logs for upstream API errors.

- Audio not generating:
  - Verify `ELEVENLABS_API_KEY` or `OPENAI_API_KEY`.
  - Check network logs for `/api/chat/` response payload.
