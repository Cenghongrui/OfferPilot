from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "http://127.0.0.1:3000"


def request(method: str, path: str, body: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("code") != 0:
        raise AssertionError(f"{method} {path} failed: {payload}")
    return payload["data"]


def wait_for_server() -> None:
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            request("GET", "/health")
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.5)
    raise RuntimeError("Backend did not become ready")


def main() -> None:
    wait_for_server()
    unique = int(time.time())
    registered = request(
        "POST",
        "/auth/register",
        {"name": "Smoke User", "email": f"smoke-{unique}@example.com", "password": "123456"},
    )
    token = registered["accessToken"]
    request("GET", "/users/me", token=token)
    questions = request("GET", "/questions?page=1&pageSize=10", token=token)
    if questions["list"]:
        raise AssertionError("New users should start with an empty question bank")
    first_question = request(
        "POST",
        "/questions",
        {
            "title": "Vue3 响应式原理是什么？",
            "category": "Vue",
            "difficulty": "medium",
            "tags": ["Vue", "响应式"],
            "answer": "Vue3 通过 Proxy 进行依赖收集和触发更新。",
            "followUps": ["ref 和 reactive 有什么区别？"],
            "pitfalls": ["不要忽略依赖收集和触发更新是两个阶段。"],
            "mastered": False,
            "starred": False,
            "note": "",
            "lastReviewedAt": "",
        },
        token,
    )
    request("PATCH", f"/questions/{first_question['id']}/star", {"starred": not first_question.get("starred", False)}, token)
    apps = request("GET", "/applications", token=token)
    if apps["list"]:
        raise AssertionError("New users should start with an empty application board")
    first_app = request(
        "POST",
        "/applications",
        {"company": "测试公司", "role": "前端实习生", "city": "上海", "source": "官网", "stage": "applied"},
        token,
    )
    request("PATCH", f"/applications/{first_app['id']}/move", {"toStage": "offer", "sortOrder": 1000}, token)
    session = request(
        "POST",
        "/mock-interview/sessions",
        {"mode": "Vue 专项面", "position": "前端开发实习生", "techStack": "Vue3、JavaScript", "questionIds": ["mock_q_vue"]},
        token,
    )
    report = request(
        "POST",
        f"/mock-interview/sessions/{session['id']}/report",
        {"questionId": "mock_q_vue", "questionTitle": "Vue3 响应式原理", "answerNote": "我会从 Proxy、track 和 trigger 三步回答。", "duration": 3},
        token,
    )
    if not report.get("suggestion"):
        raise AssertionError("Mock report suggestion is missing")
    print("OfferPilot backend smoke test passed")


if __name__ == "__main__":
    main()
