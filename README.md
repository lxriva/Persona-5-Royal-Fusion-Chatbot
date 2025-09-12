# Avi-AI-1 P5R Fusion Chatbot

A lightweight web app that answers Persona 5 Royal fusion questions using a small retrieval index (FAISS) and an LLM.

**Frontend**: Static docs/ (served by GitHub Pages)  
**Backend**: FastAPI API (deployed on Render)

**Goal**: Keep backend code/keys off the client while letting the site be public.

## 🔗 Live URLs

- **Frontend (GitHub Pages)**: https://lxriva.github.io/Avi-AI-1-P5R-Fusion-Chatbot
- **Backend (Render)**: https://avi-ai-1-p5r-fusion-chatbot.onrender.com

> **Note**: Visiting the backend root may return 404; use `GET /health` or `POST /ask`.

## 🔧 How it Works

1. The browser posts your question to `POST /ask` on the backend
2. The backend loads a local FAISS index (`Backend/vectorstore/`) and retrieves relevant chunks
3. A small LLM (e.g., gpt-4o-mini) answers using the retrieved context
4. The page renders the answer

## 📁 Repository Structure

```
.
├─ Backend/                # FastAPI service (Render)
│  ├─ server.py            # exposes: GET /health, POST /ask
│  ├─ requirements.txt     # Python deps (Py 3.13–friendly pins)
│  ├─ Procfile             # web: uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
│  └─ vectorstore/         # FAISS files: index.faiss + index.pkl
│
└─ docs/                   # Frontend (GitHub Pages)
   ├─ index.html           # sets window.BACKEND_URL to the Render URL
   ├─ style.css
   ├─ Persona 5 Royal Fusion Help Chatbot.png
   └─ background.jpg

```

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.13 (or 3.11)
- An OpenAI API key with access to your chosen model

### 1. Backend — Run Locally

```bash
# From repo root
cd Backend

# Create virtual environment
python -m venv .venv        # Windows: py -3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1

# Install dependencies (3.13-friendly pins in requirements.txt)
pip install -r requirements.txt

# Set environment variables (or create a local .env that you DO NOT commit)
# OPENAI_API_KEY=sk-...
# ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000

# Run API
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 2. Frontend — Point to Your Local API

In `docs/index.html`, near the top:

```html
<script>window.BACKEND_URL = "http://127.0.0.1:8000";</script>
```

Now open `docs/index.html` in a browser (or serve the folder with any static server).

### 🧪 Smoke Tests

```bash
# Backend health check
curl http://127.0.0.1:8000/health

# Test fusion question
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I fuse Yoshitsune?"}'
```

## 🚢 Deployment

### Backend (Render)

1. Create Web Service → connect this repo
2. **Root Directory**: `Backend` (case-sensitive)
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - `OPENAI_API_KEY` = your key
   - `ALLOWED_ORIGINS` = `https://lxriva.github.io`
6. Deploy and health check: `GET /health` should return `{"ok": true}`

### Frontend (GitHub Pages)

1. Keep the static site under `docs/`
2. Repo → Settings → Pages → Source: Deploy from a branch → Branch: `main` • Folder: `/docs`
3. In `docs/index.html`, set:
   ```html
   <script>window.BACKEND_URL = "https://avi-ai-1-p5r-fusion-chatbot.onrender.com";</script>
   ```

## 📚 API Reference

### `GET /health`

Returns health status of the backend.

**Response**:
```json
{"ok": true}
```

### `POST /ask`

Submit a Persona 5 Royal fusion question.

**Request Body**:
```json
{"question": "How do I fuse Yoshitsune?"}
```

**Response**:
```json
{"answer": "..."}
```

## 🐛 Troubleshooting

### 404 at root (`GET /`)
That's expected unless you added a home route. Use `/health` and `/ask`.

### CORS error in the browser
Ensure `ALLOWED_ORIGINS` includes exactly your site origin, e.g. `https://lxriva.github.io`.

### FAISS or NumPy conflicts
- **Python 3.13**: Use `faiss-cpu==1.12.0` and `numpy>=2,<3`, and `langchain>=0.2.20` (+ langchain-community)
- **Python 3.11**: Use `faiss-cpu==1.7.4` and `numpy<2.0.0`, and `langchain==0.2.12`

### Vector store missing
The backend must have `Backend/vectorstore/index.faiss` and `index.pkl`. Rebuild or include them in Git.

## 🛡️ Security Notes (Simple Hardening)

- **Never commit `.env` or API keys**. Use environment variables on the host.
- **Optional**: Add a shared header for the frontend only:
  - Backend checks `X-API-Key: <token>`
  - Host sets `PUBLIC_FRONTEND_TOKEN=<token>`
  - Frontend includes that header in fetch requests

## 📋 Python & Dependencies Notes

This repo is configured for Python 3.13 on Render with:

```
numpy>=2.0.0,<3.0.0
faiss-cpu==1.12.0
langchain>=0.2.20
langchain-community>=0.2.20
langchain-openai>=0.1.21
```

If you prefer Python 3.11, adjust requirements accordingly (`faiss-cpu==1.7.4`, `numpy<2.0.0`, `langchain==0.2.12`) and pin via `Backend/runtime.txt` → `python-3.11.9`.

## 🙏 Credits & Attribution
- **Game IP**: Persona 5 Royal © ATLUS / SEGA. This project is a fan-made, non-commercial tool for educational purposes.
- **Data files**: This project uses P5R data files provided in this repository.
  - Original compilation/formatting credit: the open-source project [persona5_calculator](https://github.com/chinhodado/persona5_calculator) by chinhodado and contributors, and/or the original creator credited in the included files.
  - If you are the original author of any data included here and want attribution adjusted, please open an issue or PR.
- **Project setup**: Frontend/Backend split authored by the repository owner; LLM-backed retrieval with FAISS.

## 📄 License

This repository is shared for educational use. Persona 5 Royal assets/data remain the property of their respective owners. See individual file headers for any additional attributions or license terms.

- **Header title banner**: Created using the Persona 5 title generator by lzxhahaha — https://lzxhahaha.github.io/persona5 (credit required for use of this tool).
- **Game IP**: Persona 5 Royal © ATLUS / SEGA. This project is a fan-made, non-commercial tool for educational purposes.
- **Data files**: This project uses P5R data files provided in this repository.
  - Original compilation/formatting credit: the open-source project [persona5_calculator](https://github.com/chinhodado/persona5_calculator) by chinhodado and contributors, and/or the original creator credited in the included files.
  - If you are the original author of any data included here and want attribution adjusted, please open an issue or PR.
- **Project setup**: Frontend/Backend split authored by the repository owner; LLM-backed retrieval with FAISS.

## 📄 License

This repository is shared for educational use. Persona 5 Royal assets/data remain the property of their respective owners. See individual file headers for any additional attributions or license terms.
