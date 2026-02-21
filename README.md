# AI-Powered Adaptive Learning Platform

Complete full-stack project implementing adaptive learning based on Visual, Auditory, and Kinesthetic styles.

## Implemented Required Features

1. User Authentication
- Register with name, email, password
- Password hashing using Werkzeug
- JWT login/session flow
- Logout endpoint and client token cleanup

2. Learning Style Identification
- Direct style selection: Visual / Auditory / Kinesthetic
- 20-question MCQ psychological test
- Score calculation (visual/auditory/kinesthetic)
- Learning style + scores saved to database

3. Adaptive Dashboard
- Shows user name
- Shows detected style and scores
- Chatbot access
- Download history
- Practice lab access only for kinesthetic users

4. AI Chatbot (Adaptive)
- Visual responses: flow diagram + video/gif links + visual downloads
- Auditory responses: spoken-style script + audio player + audio download
- Kinesthetic responses: step-by-step tasks + starter code + practice assets
- Chat history stored in DB

5. Virtual Practice Lab (Kinesthetic only)
- Task list with starter Java code
- In-browser code editor
- Run code feature via Judge0 API (or offline simulation fallback)
- Code submission + completion status + time tracking in DB

6. Database Storage
- users
- learning_style
- chat_history
- practice_activity
- downloads

7. Downloadable Resources
- Visual: notes/video summary download
- Auditory: audio script download
- Kinesthetic: task sheet/solution download
- Download records stored and retrievable per user

8. System Flow Logic
- After login system checks learning style
- If not set, user is redirected to style selection/test
- Adaptive content generated based on style
- Chat history and downloads are persisted

## Project Structure
- `/Users/ravikantupadhyay/Documents/industry snap/backend`
- `/Users/ravikantupadhyay/Documents/industry snap/frontend`

## Backend Setup
1. `cd /Users/ravikantupadhyay/Documents/industry\ snap/backend`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env`
6. (Optional) Add Judge0 credentials in `.env` for real Java compilation
7. `python3 run.py`

Backend runs on: `http://127.0.0.1:5000`

## Frontend Setup
1. `cd /Users/ravikantupadhyay/Documents/industry\ snap/frontend`
2. `cp .env.example .env`
3. `npm install`
4. `npm run dev`

Frontend runs on: `http://127.0.0.1:5173`

## Default Credentials
No default users are pre-created. Register from UI first.

## API Overview
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`
- Style: `/api/style/questions`, `/api/style/select`, `/api/style/submit-test`, `/api/style/mine`
- Chat: `/api/chat/`, `/api/chat/history`
- Practice: `/api/practice/tasks`, `/api/practice/run`, `/api/practice/submit`, `/api/practice/mine`
- Downloads: `/api/downloads/`, `/api/downloads/mine`, `/api/downloads/file/<download_id>`

## Notes
- Real LLM/TTS integration can be plugged into `backend/app/services/chatbot_service.py`.
- Judge0 integration is already wired in `backend/app/services/lab_runner.py`.
- Without Judge0 keys, run-code uses a simulation fallback for offline demo.
