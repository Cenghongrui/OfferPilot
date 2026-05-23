import os
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = AGENT_DIR.parent


def _load_env() -> None:
    """Load environment variables from agent/.env and project .env files."""
    for env_path in (AGENT_DIR / ".env", PROJECT_DIR / ".env"):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_env()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_KEY", os.getenv("DEEPSEEK_APIKEY", os.getenv("API_KEY", ""))))
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")
# Normalize: strip /chat/completions suffix for OpenAI SDK compatibility
if DEEPSEEK_API_URL and DEEPSEEK_API_URL.endswith("/chat/completions"):
    DEEPSEEK_API_URL = DEEPSEEK_API_URL.replace("/chat/completions", "")
# The OpenAI SDK appends /chat/completions and /v1 automatically when needed
DEEPSEEK_TEMPERATURE_QUESTION = float(os.getenv("DEEPSEEK_TEMPERATURE_QUESTION", "0.7"))
DEEPSEEK_TEMPERATURE_REPORT = float(os.getenv("DEEPSEEK_TEMPERATURE_REPORT", "0.4"))
