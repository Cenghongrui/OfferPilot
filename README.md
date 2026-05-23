# OfferPilot

OfferPilot is a Vue 3 interview-prep workbench with a local FastAPI + SQLite backend.

## Backend setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Local development

Start the API:

```powershell
npm.cmd run api
```

Start the Vue app in another terminal:

```powershell
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. The frontend proxies `/api` requests to `http://127.0.0.1:3000`.

The SQLite database is created automatically at `backend/offerpilot.sqlite3`.

For AI mock interviews, add your DeepSeek key to a local `.env` file:

```powershell
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseekv4-flash
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
```
