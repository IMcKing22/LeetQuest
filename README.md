# LeetQuest

LeetQuest is a story-driven LeetCode training adventure. Pick a topic, choose your path, and solve algorithm problems while your in‑game guide (Bella) narrates your journey, offers code reviews, and celebrates your wins.

## What It Does
- Interactive branching story that adapts to your topic and progress
- Auto-fetches curated LeetCode problems by topic/difficulty
- Starter function signatures aligned with canonical problems
- Built-in example test cases and a Judge0-powered code runner
- Bella, your AI guide, provides code reviews and chat help
- Progression (Easy → Medium → Hard) with story continuations

## Tech Stack
- Frontend: React + Vite, Monaco Editor
- Backend: Flask + Flask‑CORS, Requests
- AI: OpenAI Responses API (with graceful fallbacks)
- Execution: Judge0 CE API
- Data: CSV-backed metadata + robust fallbacks
- Deploy: Vercel (frontend), Render (backend/gunicorn)

## Architecture
- `frontend/`
  - `src/components/ChoiceScreen.jsx`: Starts story, shows path options, passes `sessionId` forward
  - `src/components/ProblemScreen.jsx`: Problem content, Monaco editor, run/submit, Bella chat
  - Uses `VITE_API_BASE` for API calls
- `app.py`
  - Story: `POST /api/start`, `POST /api/choices`, `/api/story/*-completion`
  - Problems: `/api/leetcode/*` (topic, difficulty, slug)
  - Execute: `POST /api/leetcode/execute` (Judge0 wrapper)
  - Bella: `POST /api/bella/review`, `POST /api/bella/chat`
  - CORS origins configurable via `BACKEND_ALLOWED_ORIGINS`

## AI Behavior
- If `OPENAI_API_KEY` is set (backend), stories and Bella responses are generated
- If quota/key unavailable, smart heuristic fallbacks keep UX flowing

## Run Locally
Backend
- `pip install -r requirements.txt`
- `.env` (untracked): `OPENAI_API_KEY=...` (optional)
- `python app.py` (dev) or `gunicorn app:app --bind 0.0.0.0:5002`

Frontend
- `cd frontend && npm i`
- `.env.local`: `VITE_API_BASE=http://localhost:5002`
- `npm run dev`

## Deploy
Backend (Render)
- Procfile: `web: gunicorn app:app --bind 0.0.0.0:$PORT`
- requirements.txt includes `gunicorn` and `pandas==1.5.3`
- Recommended env vars: `OPENAI_API_KEY`, `BACKEND_ALLOWED_ORIGINS`, `PYTHON_VERSION=3.11.9`

Frontend (Vercel)
- Set `VITE_API_BASE` to your Render URL
- Build: `npm run build`, Output: `dist`

## Notes
- Secrets are git‑ignored (.env). Don’t push API keys to the repo
- Judge0 CE is used for execution; outputs are normalized before comparison

Sharpen your blade, choose your path, and let the story carry you to mastery. 🗡️📚✨
