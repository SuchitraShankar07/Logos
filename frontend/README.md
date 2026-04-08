# Logos Frontend

React + Vite + Tailwind UI for the Logos debugging backend.

## Setup

```bash
cd frontend
npm install
```

## Run (Dev)

```bash
npm run dev
```

Frontend runs at `http://localhost:5173` by default.

## Connect to Backend

Start backend first (from repo root):

```bash
source .venv/bin/activate
python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

Then run frontend. By default, frontend calls `/debug` and uses Vite proxy to route to `http://127.0.0.1:8000/debug`.

Optional direct API URL override:

```bash
VITE_DEBUG_API_URL=http://127.0.0.1:8000/debug npm run dev
```

## Build

```bash
npm run build
npm run preview
```
