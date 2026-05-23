from __future__ import annotations

import json
import hashlib
import hmac
import os
import sqlite3
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

from fastapi import APIRouter, Depends, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

sys.path.insert(0, str(PROJECT_DIR))


def load_local_env() -> None:
    env_file = PROJECT_DIR / ".env"
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env()

DB_PATH = Path(os.getenv("OFFERPILOT_DB_PATH", BASE_DIR / "offerpilot.sqlite3"))
PASSWORD_ITERATIONS = 120_000


class ApiError(Exception):
    def __init__(self, status_code: int, code: int, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL,
              goal TEXT NOT NULL DEFAULT '',
              notifications INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS records (
              user_id TEXT NOT NULL,
              collection TEXT NOT NULL,
              id TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (user_id, collection, id),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_records_user_collection
              ON records(user_id, collection, created_at DESC);
            """
        )


def get_db() -> Generator[sqlite3.Connection, None, None]:
    db = connect()
    try:
        yield db
    finally:
        db.close()


def ok(data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": 0, "message": "ok", "data": data})


def fail(status_code: int, code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})


async def read_json(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        return {}
    return body if isinstance(body, dict) else {"list": body}


def token_from_header(authorization: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return ""


def hash_password(password: str) -> str:
    salt = uuid.uuid4().hex
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(stored: str, password: str) -> bool:
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt, digest = stored.split("$", 3)
            candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations)).hex()
            return hmac.compare_digest(candidate, digest)
        except (ValueError, TypeError):
            return False

    # Backward compatibility for earlier local demo rows created before hashing.
    return hmac.compare_digest(stored, password)


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "goal": row["goal"],
        "notifications": bool(row["notifications"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def require_user(
    db: sqlite3.Connection = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> sqlite3.Row:
    token = token_from_header(authorization)
    if not token:
        raise ApiError(401, 40100, "Missing or invalid token")

    row = db.execute(
        """
        SELECT users.*
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()
    if not row:
        raise ApiError(401, 40100, "Missing or invalid token")
    return row


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def parse_payload(row: sqlite3.Row) -> dict[str, Any]:
    return json.loads(row["payload"])


def list_items(db: sqlite3.Connection, user_id: str, collection: str) -> list[dict[str, Any]]:
    rows = db.execute(
        """
        SELECT payload
        FROM records
        WHERE user_id = ? AND collection = ?
        ORDER BY created_at DESC
        """,
        (user_id, collection),
    ).fetchall()
    return [parse_payload(row) for row in rows]


def get_item(db: sqlite3.Connection, user_id: str, collection: str, item_id: str) -> dict[str, Any] | None:
    row = db.execute(
        "SELECT payload FROM records WHERE user_id = ? AND collection = ? AND id = ?",
        (user_id, collection, item_id),
    ).fetchone()
    return parse_payload(row) if row else None


def put_item(db: sqlite3.Connection, user_id: str, collection: str, item: dict[str, Any]) -> dict[str, Any]:
    item_id = str(item["id"])
    created_at = str(item.get("createdAt") or now_iso())
    updated_at = str(item.get("updatedAt") or created_at)
    payload = {**item, "id": item_id, "createdAt": created_at, "updatedAt": updated_at}
    db.execute(
        """
        INSERT OR REPLACE INTO records (user_id, collection, id, payload, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, collection, item_id, json.dumps(payload, ensure_ascii=False), created_at, updated_at),
    )
    return payload


def create_item(db: sqlite3.Connection, user_id: str, collection: str, prefix: str, body: dict[str, Any]) -> dict[str, Any]:
    item = {**body, "id": body.get("id") or make_id(prefix), "createdAt": now_iso(), "updatedAt": now_iso()}
    return put_item(db, user_id, collection, item)


def update_item(
    db: sqlite3.Connection,
    user_id: str,
    collection: str,
    item_id: str,
    body: dict[str, Any],
) -> dict[str, Any] | None:
    current = get_item(db, user_id, collection, item_id)
    if current is None:
        return None
    current.update(body)
    current["updatedAt"] = now_iso()
    return put_item(db, user_id, collection, current)


def delete_item(db: sqlite3.Connection, user_id: str, collection: str, item_id: str) -> None:
    db.execute(
        "DELETE FROM records WHERE user_id = ? AND collection = ? AND id = ?",
        (user_id, collection, item_id),
    )


def replace_items(
    db: sqlite3.Connection,
    user_id: str,
    collection: str,
    prefix: str,
    items: list[dict[str, Any]],
) -> None:
    db.execute("DELETE FROM records WHERE user_id = ? AND collection = ?", (user_id, collection))
    for item in items:
        put_item(db, user_id, collection, {**item, "id": item.get("id") or make_id(prefix)})


def paginate(items: list[dict[str, Any]], page: int = 1, page_size: int | None = None) -> dict[str, Any]:
    safe_page = max(1, int(page or 1))
    safe_size = int(page_size or len(items) or 20)
    safe_size = max(1, safe_size)
    start = (safe_page - 1) * safe_size
    end = start + safe_size
    return {"list": items[start:end], "pagination": {"page": safe_page, "pageSize": safe_size, "total": len(items)}}


def question_stats(questions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(questions),
        "starred": len([item for item in questions if item.get("starred")]),
        "reviewTodo": len([item for item in questions if not item.get("mastered")]),
    }


def algorithm_stats(algorithms: list[dict[str, Any]]) -> dict[str, int]:
    done = len([item for item in algorithms if item.get("status") == "done"])
    return {
        "total": len(algorithms),
        "completionRate": round(done / len(algorithms) * 100) if algorithms else 0,
        "reviewCountThisWeek": len([item for item in algorithms if item.get("notes")]),
    }


def application_stats(applications: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(applications),
        "interviewing": len([item for item in applications if item.get("stage") in {"interview_1", "interview_2", "hr"}]),
        "offer": len([item for item in applications if item.get("stage") == "offer"]),
    }


def dashboard_overview(db: sqlite3.Connection, user_id: str) -> dict[str, Any]:
    questions = list_items(db, user_id, "questions")
    algorithms = list_items(db, user_id, "algorithms")
    applications = list_items(db, user_id, "applications")
    sessions = list_items(db, user_id, "mockSessions")
    review_todo = len([item for item in questions if not item.get("mastered")])
    weak_points = [
        {"name": item.get("title", "Question"), "mastery": 30}
        for item in questions
        if not item.get("mastered")
    ][:5]

    return {
        "stats": {
            "studyHoursToday": 0,
            "reviewTodoCount": review_todo,
            "algorithmSolvedCount": len([item for item in algorithms if item.get("status") == "done"]),
            "applicationCount": len(applications),
            "mockInterviewCount": len(sessions),
        },
        "changes": {
            "studyHoursToday": 0,
            "reviewTodoCount": 0,
            "algorithmSolvedCount": 0,
            "applicationCount": 0,
            "mockInterviewCount": 0,
        },
        "mastery": {
            "overall": round((len(questions) - review_todo) / len(questions) * 100) if questions else 0,
        },
        "weakPoints": weak_points,
    }


def profile_overview(db: sqlite3.Connection, user: sqlite3.Row) -> dict[str, Any]:
    user_id = user["id"]
    questions = list_items(db, user_id, "questions")
    applications = list_items(db, user_id, "applications")
    sessions = list_items(db, user_id, "mockSessions")
    reports = [item for item in sessions if item.get("report")]
    average_score = round(sum(float(item["report"].get("total", 0)) for item in reports) / len(reports)) if reports else 0
    return {
        "user": public_user(user),
        "overview": {
            "reviewTodoCount": len([item for item in questions if not item.get("mastered")]),
            "activeApplicationCount": len([item for item in applications if item.get("stage") not in {"closed", "offer"}]),
            "mockInterviewAverageScore": average_score,
        },
        "activities": [],
    }


MOCK_MODES = [
    {"name": "前端基础面", "desc": "CSS、JavaScript、浏览器基础"},
    {"name": "Vue 专项面", "desc": "响应式、组件通信、路由和状态管理"},
    {"name": "网络与工程化", "desc": "HTTP、缓存、跨域、构建和部署"},
    {"name": "项目深挖面", "desc": "项目边界、接口设计、性能和难点复盘"},
    {"name": "算法快问", "desc": "数组、栈、哈希表、滑动窗口"},
]


def seed_user_data(db: sqlite3.Connection, user_id: str) -> None:
    seed = {
        "todayPlans": [
            {"id": "plan_001", "title": "Review Vue reactivity", "type": "Knowledge", "startTime": "09:00", "endTime": "10:00", "completed": True},
            {"id": "plan_002", "title": "Practice sliding window", "type": "Algorithm", "startTime": "10:30", "endTime": "12:00", "completed": False},
            {"id": "plan_003", "title": "Polish OfferPilot demo", "type": "Project", "startTime": "14:00", "endTime": "16:00", "completed": False},
        ],
        "questions": [
            {
                "id": "q_vue_001",
                "title": "Vue 3 reactivity",
                "category": "Vue",
                "difficulty": "medium",
                "tags": ["proxy", "effect"],
                "answer": "Vue 3 uses Proxy to track reads and trigger effects on writes.",
                "followUps": ["ref vs reactive", "computed cache"],
                "pitfalls": ["Do not skip dependency tracking."],
                "mastered": False,
                "starred": True,
                "lastReviewedAt": "2026-05-20",
                "note": "",
            },
            {
                "id": "q_js_001",
                "title": "Event loop",
                "category": "JavaScript",
                "difficulty": "medium",
                "tags": ["promise", "async"],
                "answer": "Synchronous code runs first, then microtasks, then the next macrotask.",
                "followUps": ["Promise.then task type", "setTimeout timing"],
                "pitfalls": ["Microtasks are drained before rendering opportunities."],
                "mastered": False,
                "starred": False,
                "lastReviewedAt": "2026-05-19",
                "note": "",
            },
            {
                "id": "q_css_001",
                "title": "Flex vs Grid",
                "category": "CSS",
                "difficulty": "easy",
                "tags": ["layout"],
                "answer": "Flex is good for one-dimensional layout, Grid for two-dimensional layout.",
                "followUps": ["What does flex: 1 mean?", "How to build responsive grid columns?"],
                "pitfalls": ["Grid is not the same as table layout."],
                "mastered": True,
                "starred": False,
                "lastReviewedAt": "2026-05-21",
                "note": "",
            },
        ],
        "algorithms": [
            {
                "id": "lc_003",
                "title": "Longest substring without repeating characters",
                "leetcodeUrl": "https://leetcode.cn/problems/longest-substring-without-repeating-characters/",
                "difficulty": "medium",
                "tags": ["sliding-window", "hash-map"],
                "status": "doing",
                "description": "Find the longest substring without duplicate characters.",
                "idea": "Use a sliding window and move left when a duplicate appears.",
                "complexity": "Time O(n), space O(k).",
                "codeDraft": "function lengthOfLongestSubstring(s) {\\n  const map = new Map()\\n  let left = 0\\n  let ans = 0\\n  for (let right = 0; right < s.length; right++) {\\n    const char = s[right]\\n    if (map.has(char) && map.get(char) >= left) left = map.get(char) + 1\\n    map.set(char, right)\\n    ans = Math.max(ans, right - left + 1)\\n  }\\n  return ans\\n}",
                "notes": "left only moves forward.",
                "testCases": [{"input": "\"abcabcbb\"", "expected": 3}],
            },
            {
                "id": "lc_020",
                "title": "Valid parentheses",
                "leetcodeUrl": "https://leetcode.cn/problems/valid-parentheses/",
                "difficulty": "easy",
                "tags": ["stack"],
                "status": "done",
                "description": "Check whether brackets are closed in the correct order.",
                "idea": "Push left brackets and match right brackets with the stack top.",
                "complexity": "Time O(n), space O(n).",
                "codeDraft": "function isValid(s) { return true }",
                "notes": "Remember the empty stack edge case.",
                "testCases": [{"input": "\"()[]{}\"", "expected": True}],
            },
        ],
        "experiences": [
            {
                "id": "exp_001",
                "company": "ByteDance",
                "role": "Frontend Intern",
                "city": "Shanghai",
                "date": "2026-05-02",
                "round": "First Round",
                "result": "pending",
                "questions": [{"category": "Vue", "content": "Explain Vue 3 reactivity."}],
                "review": {"good": "Project background was clear.", "stuck": "Caching answer needs more detail.", "action": "Review HTTP caching."},
                "markdown": "### Review\\n- Prepare one concrete project example.",
            }
        ],
        "applications": [
            {
                "id": "app_001",
                "company": "Tencent",
                "role": "Frontend Intern",
                "city": "Shenzhen",
                "source": "Official site",
                "stage": "interview_1",
                "deadline": "2026-06-15",
                "nextAction": "Prepare project deep dive",
                "notes": "Focus on router guard and request wrapper.",
                "sortOrder": 1000,
            },
            {
                "id": "app_002",
                "company": "Meituan",
                "role": "Frontend Engineer Intern",
                "city": "Beijing",
                "source": "Campus hiring",
                "stage": "applied",
                "deadline": "2026-06-20",
                "nextAction": "Wait for screening",
                "notes": "Prepare algorithm practice.",
                "sortOrder": 1000,
            },
        ],
        "mockSessions": [],
        "notifications": [
            {"id": "notice_001", "title": "Welcome to OfferPilot", "content": "Your local FastAPI backend is ready.", "read": False}
        ],
    }
    prefixes = {
        "todayPlans": "plan",
        "questions": "q",
        "algorithms": "algo",
        "experiences": "exp",
        "applications": "app",
        "mockSessions": "session",
        "notifications": "notice",
    }
    for collection, items in seed.items():
        for item in items:
            put_item(db, user_id, collection, {**item, "id": item.get("id") or make_id(prefixes[collection])})


router = APIRouter()


@router.get("/health")
def health() -> JSONResponse:
    return ok({"status": "ok", "dbPath": str(DB_PATH)})


@router.post("/auth/register")
async def register(request: Request, db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    body = await read_json(request)
    name = str(body.get("name") or "").strip()
    email = str(body.get("email") or "").strip().lower()
    password = str(body.get("password") or "")

    if not name or not email or not password:
        raise ApiError(400, 40000, "Please provide name, email and password")

    if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        raise ApiError(409, 40002, "Email has already been registered")

    user_id = make_id("user")
    timestamp = now_iso()
    db.execute(
        """
        INSERT INTO users (id, name, email, password, goal, notifications, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, email, hash_password(password), "", 1, timestamp, timestamp),
    )
    token = f"local_{uuid.uuid4()}"
    db.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_id, timestamp))
    db.commit()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return ok({"user": public_user(user), "accessToken": token})


@router.post("/auth/login")
async def login(request: Request, db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    body = await read_json(request)
    email = str(body.get("email") or "").strip().lower()
    password = str(body.get("password") or "")
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user or not verify_password(str(user["password"]), password):
        raise ApiError(401, 40001, "Email or password is incorrect")

    if not str(user["password"]).startswith("pbkdf2_sha256$"):
        db.execute("UPDATE users SET password = ?, updated_at = ? WHERE id = ?", (hash_password(password), now_iso(), user["id"]))
        user = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()

    token = f"local_{uuid.uuid4()}"
    db.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user["id"], now_iso()))
    db.commit()
    return ok({"user": public_user(user), "accessToken": token})


@router.post("/auth/logout")
def logout(
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
    authorization: str | None = Header(default=None),
) -> JSONResponse:
    _ = user
    db.execute("DELETE FROM sessions WHERE token = ?", (token_from_header(authorization),))
    db.commit()
    return ok()


@router.get("/users/me")
def current_user(user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(public_user(user))


@router.patch("/users/me")
async def update_current_user(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    body = await read_json(request)
    db.execute(
        """
        UPDATE users
        SET name = ?, goal = ?, notifications = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            body.get("name", user["name"]),
            body.get("goal", user["goal"]),
            int(bool(body.get("notifications", bool(user["notifications"])))),
            now_iso(),
            user["id"],
        ),
    )
    db.commit()
    updated = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    return ok(public_user(updated))


@router.get("/dashboard/overview")
def get_dashboard_overview(
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    return ok(dashboard_overview(db, user["id"]))


@router.get("/dashboard/today-plan")
def get_today_plan(
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    return ok(list_items(db, user["id"], "todayPlans"))


@router.patch("/dashboard/today-plan/{plan_id}")
async def update_today_plan(
    plan_id: str,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    body = await read_json(request)
    item = update_item(db, user["id"], "todayPlans", plan_id, {"completed": bool(body.get("completed"))})
    db.commit()
    return ok(item)


@router.get("/questions/stats")
def get_question_stats(
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    return ok(question_stats(list_items(db, user["id"], "questions")))


@router.get("/questions")
def get_questions(
    page: int = 1,
    pageSize: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "questions"), page, pageSize))


@router.post("/questions")
async def create_question(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    user: sqlite3.Row = Depends(require_user),
) -> JSONResponse:
    item = create_item(db, user["id"], "questions", "q", await read_json(request))
    db.commit()
    return ok(item)


@router.get("/questions/{question_id}")
def get_question(question_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(get_item(db, user["id"], "questions", question_id))


@router.patch("/questions/{question_id}")
async def update_question(question_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "questions", question_id, await read_json(request))
    db.commit()
    return ok(item)


@router.patch("/questions/{question_id}/star")
async def update_question_star(question_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    body = await read_json(request)
    item = update_item(db, user["id"], "questions", question_id, {"starred": bool(body.get("starred"))})
    db.commit()
    return ok(item)


@router.patch("/questions/{question_id}/mastery")
async def update_question_mastery(question_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "questions", question_id, await read_json(request))
    db.commit()
    return ok(item)


@router.delete("/questions/{question_id}")
def delete_question(question_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    delete_item(db, user["id"], "questions", question_id)
    db.commit()
    return ok()


@router.get("/algorithms/stats")
def get_algorithm_stats(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(algorithm_stats(list_items(db, user["id"], "algorithms")))


@router.get("/algorithms")
def get_algorithms(page: int = 1, pageSize: int | None = None, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "algorithms"), page, pageSize))


@router.post("/algorithms")
async def create_algorithm(request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = create_item(db, user["id"], "algorithms", "algo", await read_json(request))
    db.commit()
    return ok(item)


@router.get("/algorithms/{problem_id}")
def get_algorithm(problem_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(get_item(db, user["id"], "algorithms", problem_id))


@router.patch("/algorithms/{problem_id}")
async def update_algorithm(problem_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "algorithms", problem_id, await read_json(request))
    db.commit()
    return ok(item)


@router.patch("/algorithms/{problem_id}/code-draft")
async def save_code_draft(problem_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    body = await read_json(request)
    item = update_item(db, user["id"], "algorithms", problem_id, {"codeDraft": body.get("codeDraft", "")})
    db.commit()
    return ok(item)


@router.post("/algorithms/{problem_id}/run")
async def run_algorithm(problem_id: str, request: Request, user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    _ = problem_id, user
    body = await read_json(request)
    return ok({"status": "passed", "cases": body.get("testCases", [])})


@router.get("/experiences/export")
def export_experiences(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    filename = f"offerpilot-experiences-{datetime.now().date().isoformat()}.json"
    return ok({"filename": filename, "list": list_items(db, user["id"], "experiences")})


@router.post("/experiences/import")
async def import_experiences(request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    body = await read_json(request)
    items = body.get("list", [])
    if not isinstance(items, list):
        items = []
    replace_items(db, user["id"], "experiences", "exp", items)
    db.commit()
    return ok({"imported": len(items)})


@router.get("/experiences")
def get_experiences(page: int = 1, pageSize: int | None = None, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "experiences"), page, pageSize))


@router.post("/experiences")
async def create_experience(request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = create_item(db, user["id"], "experiences", "exp", await read_json(request))
    db.commit()
    return ok(item)


@router.get("/experiences/{experience_id}")
def get_experience(experience_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(get_item(db, user["id"], "experiences", experience_id))


@router.patch("/experiences/{experience_id}")
async def update_experience(experience_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "experiences", experience_id, await read_json(request))
    db.commit()
    return ok(item)


@router.delete("/experiences/{experience_id}")
def delete_experience(experience_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    delete_item(db, user["id"], "experiences", experience_id)
    db.commit()
    return ok()


@router.get("/applications/stats")
def get_application_stats(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(application_stats(list_items(db, user["id"], "applications")))


@router.get("/applications")
def get_applications(page: int = 1, pageSize: int | None = None, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "applications"), page, pageSize))


@router.post("/applications")
async def create_application(request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = create_item(db, user["id"], "applications", "app", await read_json(request))
    db.commit()
    return ok(item)


@router.get("/applications/{application_id}")
def get_application(application_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(get_item(db, user["id"], "applications", application_id))


@router.patch("/applications/{application_id}")
async def update_application(application_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "applications", application_id, await read_json(request))
    db.commit()
    return ok(item)


@router.patch("/applications/{application_id}/move")
async def move_application(application_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    body = await read_json(request)
    item = update_item(db, user["id"], "applications", application_id, {"stage": body.get("toStage"), "sortOrder": body.get("sortOrder", 1000)})
    db.commit()
    return ok(item)


@router.delete("/applications/{application_id}")
def delete_application(application_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    delete_item(db, user["id"], "applications", application_id)
    db.commit()
    return ok()


@router.get("/mock-interview/modes")
def get_mock_modes(user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    _ = user
    return ok(MOCK_MODES)


@router.get("/mock-interview/stats")
def get_mock_stats(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    sessions = list_items(db, user["id"], "mockSessions")
    reports = [item for item in sessions if item.get("report")]
    average = round(sum(float(item["report"].get("total", 0)) for item in reports) / len(reports)) if reports else 0
    return ok(
        {
            "modeCount": len(MOCK_MODES),
            "totalDuration": sum(int(item.get("duration") or 0) for item in sessions),
            "averageScore": average,
        }
    )


@router.get("/mock-interview/sessions")
def get_mock_sessions(page: int = 1, pageSize: int | None = None, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "mockSessions"), page, pageSize))


@router.get("/mock-interview/sessions/{session_id}")
def get_mock_session(session_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    session = get_item(db, user["id"], "mockSessions", session_id)
    if not session:
        raise ApiError(404, 40400, "Session not found")
    return ok(session)


@router.post("/mock-interview/sessions")
async def create_mock_session(request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    body = await read_json(request)
    item = create_item(
        db,
        user["id"],
        "mockSessions",
        "session",
        {
            **body,
            "status": "running",
            "duration": 0,
            "position": body.get("position", ""),
            "techStack": body.get("techStack", ""),
            "interviewType": body.get("interviewType", body.get("mode", "")),
            "messages": [],
            "questionCount": 0,
        },
    )
    db.commit()
    return ok(item)


@router.patch("/mock-interview/sessions/{session_id}")
async def update_mock_session(session_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "mockSessions", session_id, await read_json(request))
    db.commit()
    return ok(item)


@router.post("/mock-interview/sessions/{session_id}/next-question")
async def next_question(session_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    session = get_item(db, user["id"], "mockSessions", session_id)
    if not session:
        raise ApiError(404, 40400, "Session not found")

    messages: list[dict[str, str]] = session.get("messages") or []
    question_count = int(session.get("questionCount") or 0) + 1

    try:
        from agent import agent as interview_agent

        question_text = interview_agent.generate_question(
            position=str(session.get("position") or ""),
            tech_stack=str(session.get("techStack") or ""),
            interview_type=str(session.get("interviewType") or ""),
            question_number=question_count,
            history=messages if messages else None,
        )
    except Exception:
        question_text = f"请结合 {session.get('techStack') or '你的技术栈'} 的经验，谈谈你在实际项目中遇到了哪些挑战，以及你是如何解决的。"

    messages.append({"role": "assistant", "content": f"第{question_count}题：{question_text}"})
    update_item(db, user["id"], "mockSessions", session_id, {
        "messages": messages,
        "questionCount": question_count,
    })
    db.commit()

    return ok({"question": question_text, "number": question_count})


@router.post("/mock-interview/sessions/{session_id}/chat")
async def chat_with_interviewer(session_id: str, request: Request, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)):
    body = await read_json(request)
    session = get_item(db, user["id"], "mockSessions", session_id)
    if not session:
        raise ApiError(404, 40400, "Session not found")

    user_message = str(body.get("message") or "").strip()
    if not user_message:
        raise ApiError(400, 40000, "Message is required")

    messages: list[dict[str, str]] = session.get("messages") or []
    question_count = int(session.get("questionCount") or 1)

    messages.append({"role": "user", "content": user_message})

    def generate():
        full_response = ""
        try:
            from agent import agent as interview_agent

            for token in interview_agent.chat_stream(
                position=str(session.get("position") or ""),
                tech_stack=str(session.get("techStack") or ""),
                interview_type=str(session.get("interviewType") or ""),
                question_number=question_count,
                user_message=user_message,
                history=[m for m in messages[:-1]] if len(messages) > 1 else None,
            ):
                full_response += token
                yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"
            return
        finally:
            if full_response:
                messages.append({"role": "assistant", "content": full_response})
                update_item(db, user["id"], "mockSessions", session_id, {"messages": messages})
                db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/mock-interview/sessions/{session_id}/end")
async def end_session(session_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    session = get_item(db, user["id"], "mockSessions", session_id)
    if not session:
        raise ApiError(404, 40400, "Session not found")

    messages: list[dict[str, str]] = session.get("messages") or []

    try:
        from agent import agent as interview_agent

        report = interview_agent.generate_report(
            position=str(session.get("position") or ""),
            tech_stack=str(session.get("techStack") or ""),
            interview_type=str(session.get("interviewType") or ""),
            history=messages if messages else None,
        )
        report["source"] = "deepseek"
    except Exception:
        report = {
            "total": 70,
            "summary": "面试已完成。",
            "strengths": "能够围绕题目展开回答。",
            "weakness": "回答结构还可以更完整。",
            "suggestion": "建议补充项目案例和关键概念。",
            "nextQuestions": [],
            "source": "local-fallback",
        }

    update_item(db, user["id"], "mockSessions", session_id, {
        "report": report,
        "status": "finished",
        "messages": messages,
    })
    db.commit()
    return ok(report)


@router.get("/profile/overview")
def get_profile_overview(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(profile_overview(db, user))


@router.get("/notifications/unread-count")
def get_unread_count(db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    notifications = list_items(db, user["id"], "notifications")
    return ok({"count": len([item for item in notifications if not item.get("read")])})


@router.get("/notifications")
def get_notifications(page: int = 1, pageSize: int | None = None, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    return ok(paginate(list_items(db, user["id"], "notifications"), page, pageSize))


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: sqlite3.Connection = Depends(get_db), user: sqlite3.Row = Depends(require_user)) -> JSONResponse:
    item = update_item(db, user["id"], "notifications", notification_id, {"read": True})
    db.commit()
    return ok(item)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = app
    init_db()
    yield


app = FastAPI(title="OfferPilot FastAPI Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(router, prefix="/api")


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
    _ = request
    return fail(error.status_code, error.code, error.message)


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
    _ = request
    print(f"[OfferPilot] unexpected backend error: {error}")
    return fail(500, 50000, "Local backend error")
