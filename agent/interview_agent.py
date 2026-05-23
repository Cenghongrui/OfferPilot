from __future__ import annotations

import json
import re
from typing import Any, Generator

from langchain_openai import ChatOpenAI

from agent.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    DEEPSEEK_TEMPERATURE_QUESTION,
    DEEPSEEK_TEMPERATURE_REPORT,
)
from agent.prompts import (
    CHAT_SYSTEM_PROMPT,
    INTERVIEWER_SYSTEM_PROMPT,
    NEXT_QUESTION_PROMPT,
    REPORT_SYSTEM_PROMPT,
)


class InterviewAgent:
    """LangChain-based AI interview agent with conversation memory and SSE streaming.

    Maintains per-session conversation history for multi-turn interview context.
    Supports: question generation, conversational chat (streaming), and report generation.
    """

    # ------------------------------------------------------------------
    # Question generation
    # ------------------------------------------------------------------
    def generate_question(
        self,
        position: str,
        tech_stack: str,
        interview_type: str,
        question_number: int = 1,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Generate the Nth interview question as plain text.

        Args:
            position: target job title
            tech_stack: candidate tech stack
            interview_type: interview category
            question_number: 1-based question index
            history: prior conversation messages (role/content dicts)

        Returns:
            plain question text, no JSON wrapper
        """
        llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_URL,
            temperature=DEEPSEEK_TEMPERATURE_QUESTION,
        )

        system_prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            position=position or "前端开发实习生",
            tech_stack=tech_stack or "Vue3、JavaScript、CSS、HTTP",
            interview_type=interview_type or "技术面试",
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)

        user_prompt = NEXT_QUESTION_PROMPT.format(
            question_number=question_number,
            tech_stack=tech_stack or "Vue3、JavaScript、CSS、HTTP",
            position=position or "前端开发实习生",
        )
        messages.append({"role": "user", "content": user_prompt})

        response = llm.invoke(messages)
        return str(response.content).strip()

    # ------------------------------------------------------------------
    # Conversational chat (SSE streaming)
    # ------------------------------------------------------------------
    def chat_stream(
        self,
        position: str,
        tech_stack: str,
        interview_type: str,
        question_number: int,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> Generator[str, None, None]:
        """Stream a conversational response from the interviewer.

        Yields content chunks (tokens) as they arrive from the LLM.
        Use this for SSE endpoints.

        Args:
            position: target job title
            tech_stack: candidate tech stack
            interview_type: interview category
            question_number: current question number
            user_message: the candidate's latest message
            history: prior conversation messages (role/content dicts)
        """
        llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_URL,
            temperature=DEEPSEEK_TEMPERATURE_QUESTION,
            streaming=True,
        )

        system_prompt = CHAT_SYSTEM_PROMPT.format(
            position=position or "前端开发实习生",
            tech_stack=tech_stack or "Vue3、JavaScript、CSS、HTTP",
            interview_type=interview_type or "技术面试",
            question_number=question_number,
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        for chunk in llm.stream(messages):
            content = str(chunk.content) if hasattr(chunk, "content") and chunk.content else ""
            if content:
                yield content

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------
    def generate_report(
        self,
        position: str,
        tech_stack: str,
        interview_type: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Generate a final interview report based on full conversation history.

        Returns a dict with: total, summary, dimensions, strengths, weakness,
        suggestion, resources, nextQuestions
        """
        llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_URL,
            temperature=DEEPSEEK_TEMPERATURE_REPORT,
        )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        ]

        conversation_text = ""
        if history:
            for msg in history:
                role_label = "面试官" if msg["role"] == "assistant" else "候选人"
                conversation_text += f"{role_label}：{msg['content']}\n\n"

        messages.append({
            "role": "user",
            "content": (
                f"岗位：{position or '前端开发实习生'}\n"
                f"技术栈：{tech_stack or 'Vue3、JavaScript、CSS、HTTP'}\n"
                f"面试类型：{interview_type or '技术面试'}\n\n"
                f"完整面试记录：\n{conversation_text}\n\n"
                f"请生成复盘报告。"
            ),
        })

        response = llm.invoke(messages)
        try:
            data = _extract_json(str(response.content))
        except (json.JSONDecodeError, ValueError):
            return _fallback_report()

        raw_dimensions = data.get("dimensions")
        if isinstance(raw_dimensions, list) and len(raw_dimensions) == 4:
            dimensions = [
                {
                    "name": str(d.get("name", "")),
                    "score": int(d.get("score", 3)),
                    "comment": str(d.get("comment", "")),
                }
                for d in raw_dimensions
            ]
        else:
            dimensions = _fallback_dimensions()

        raw_resources = data.get("resources")
        if isinstance(raw_resources, list):
            resources = [
                {
                    "title": str(r.get("title", "")),
                    "type": str(r.get("type", "")),
                    "description": str(r.get("description", "")),
                }
                for r in raw_resources
            ]
        else:
            resources = []

        return {
            "total": int(data.get("total") or 70),
            "summary": str(data.get("summary") or "面试已完成。"),
            "dimensions": dimensions,
            "strengths": str(data.get("strengths") or "能够围绕题目展开回答。"),
            "weakness": str(data.get("weakness") or "回答结构还可以更完整。"),
            "suggestion": str(data.get("suggestion") or "建议补充项目案例和关键概念。"),
            "resources": resources,
            "nextQuestions": data.get("nextQuestions") if isinstance(data.get("nextQuestions"), list) else [],
        }


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


def _fallback_dimensions() -> list[dict[str, Any]]:
    return [
        {"name": "技术深度", "score": 3, "comment": "基本掌握核心技术概念"},
        {"name": "沟通表达", "score": 3, "comment": "回答结构基本完整"},
        {"name": "问题解决", "score": 3, "comment": "能给出合理的解决方案"},
        {"name": "实践经验", "score": 3, "comment": "有一定项目经验积累"},
    ]


def _fallback_report() -> dict[str, Any]:
    return {
        "total": 70,
        "summary": "面试已完成，以下是基于对话记录的评估。",
        "dimensions": _fallback_dimensions(),
        "strengths": "能够围绕题目展开回答。",
        "weakness": "回答结构还可以更完整。",
        "suggestion": "建议补充项目案例和关键概念。",
        "resources": [],
        "nextQuestions": [],
    }


agent = InterviewAgent()
