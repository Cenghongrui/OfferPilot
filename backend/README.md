# OfferPilot FastAPI Backend

Local backend for the Vue demo.

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Run

```powershell
npm.cmd run api
```

The API listens on `http://127.0.0.1:3000`. The Vite dev server proxies `/api` to this backend.

SQLite data is stored at `backend/offerpilot.sqlite3` by default. Override it with `OFFERPILOT_DB_PATH` if needed.

## DeepSeek

Create a local `.env` file in the project root:

```powershell
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseekv4-flash
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
```

The backend loads `.env` on startup. Restart `npm.cmd run api` after changing the key.
