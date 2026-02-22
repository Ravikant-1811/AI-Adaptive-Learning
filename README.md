# AI-Powered Adaptive Learning Platform

Complete full-stack project implementing adaptive learning based on Visual, Auditory, and Kinesthetic styles.

## Final Feature Checklist (As Required)

### 1. User Authentication
- User registration (`name`, `email`, `password`)
- Password hashing (Werkzeug hash)
- JWT login/session flow
- Logout endpoint + client-side token clear

### 2. Learning Style Identification
- Option 1: Direct selection (`Visual`, `Auditory`, `Kinesthetic`)
- Option 2: MCQ psychological test (`20` questions)
- AI-generated test mode (auto-generated questions with fallback)
- Score calculation + style detection
- Learning style and scores stored in DB

### 3. Adaptive Dashboard
- Shows user name
- Shows detected learning style and scores
- Chatbot access
- Download history
- Practice lab access (kinesthetic)

### 4. AI Chatbot (Adaptive Response)
- Style-aware responses:
  - Visual: diagram + video/GIF support + downloadable notes
  - Auditory: audio-style script + audio player + downloadable audio
  - Kinesthetic: guided coding/task response + practice workflow
- Chat history persisted
- Auto AI learning pack generated per ask:
  - PDF notes
  - Audio script / audio file flow
  - Task sheet
  - Solution

### 5. Virtual Practice Lab (Kinesthetic)
- In-browser Java code editor
- Topic-linked tasks (AI from latest chat topic with fallback task bank)
- Run code feature (Judge0 + resilient simulation fallback)
- Code submission
- Completion status tracking
- Time spent tracking

### 6. Database Storage
- `users`
- `learning_style`
- `chat_history`
- `practice_activity`
- `downloads`

### 7. Downloadable Learning Resources
- Visual: notes + video-style content
- Auditory: audio file/script
- Kinesthetic: task sheet + solution
- Download metadata stored per user

### 8. System Flow Logic
- On login: checks learning style
- If style missing: redirects to style test/selection
- Generates style-adaptive AI content
- Saves chat history
- Saves downloads

## Project Structure
- `/Users/ravikantupadhyay/Documents/industry snap/backend`
- `/Users/ravikantupadhyay/Documents/industry snap/frontend`

## Backend Setup
1. `cd /Users/ravikantupadhyay/Documents/industry\ snap/backend`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env`
6. Add `OPENAI_API_KEY` in `.env` to enable ChatGPT-based questionnaire and chatbot
7. (Optional) Add `OPENAI_TTS_MODEL` and `OPENAI_TTS_VOICE` for audio generation
8. (Optional) Add Judge0 credentials in `.env` for real Java compilation
9. `python3 run.py`

Backend runs on: `http://127.0.0.1:5001`

## Frontend Setup
1. `cd /Users/ravikantupadhyay/Documents/industry\ snap/frontend`
2. `cp .env.example .env`
3. `npm install`
4. `npm run dev`

Frontend runs on: `http://127.0.0.1:5173`

## Default Credentials
No default users are pre-created. Register from UI first.

## API Overview
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/auth/forgot-password`, `/api/auth/reset-password`
- Style: `/api/style/questions`, `/api/style/generate-questions`, `/api/style/select`, `/api/style/submit-test`, `/api/style/mine`
- Chat: `/api/chat/`, `/api/chat/history`
- Practice: `/api/practice/tasks`, `/api/practice/run`, `/api/practice/submit`, `/api/practice/mine`
- Downloads: `/api/downloads/`, `/api/downloads/mine`, `/api/downloads/file/<download_id>`

## Notes
- ChatGPT integration is implemented in `backend/app/services/openai_service.py`.
- AI learning asset generation is implemented in `backend/app/services/adaptive_content_service.py`.
- If `OPENAI_API_KEY` is missing, the app falls back to default static questions and fallback chatbot content.
- Judge0 integration is already wired in `backend/app/services/lab_runner.py`.
- Without Judge0 keys, run-code uses a simulation fallback for offline demo.
- API root health checks:
  - `GET /` returns API info
  - `GET /api/health` returns service health
