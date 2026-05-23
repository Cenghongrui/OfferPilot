import json
import re
from typing import Any

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agent.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    DEEPSEEK_TEMPERATURE_QUESTION,
    DEEPSEEK_TEMPERATURE_REPORT,
)
from agent.prompts import (
    QUESTION_SYSTEM_PROMPT,
    QUESTION_USER_TEMPLATE,
    REPORT_SYSTEM_PROMPT,
    REPORT_USER_TEMPLATE,
)


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON object from model response text."""
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


def _create_llm(temperature: float = 0.7) -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for DeepSeek API."""
    return ChatOpenAI(
        model=DEEPSEEK_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_API_URL,
        temperature=temperature,
    )


@tool
def generate_question(position: str, tech_stack: str, interview_type: str) -> dict[str, Any]:
    """根据岗位、技术栈和面试类型生成一道模拟面试题。

    Args:
        position: 面试岗位，如"前端开发实习生"
        tech_stack: 技术栈，如"Vue3、JavaScript、CSS"
        interview_type: 面试类型，如"Vue 专项面"

    Returns:
        包含 title、prompt、followUps、hint、evaluationFocus 的题目字典
    """
    llm = _create_llm(temperature=DEEPSEEK_TEMPERATURE_QUESTION)
    user_prompt = QUESTION_USER_TEMPLATE.format(
        position=position or "前端开发实习生",
        tech_stack=tech_stack or "Vue3、JavaScript、CSS、HTTP",
        interview_type=interview_type or "技术面试",
    )
    response = llm.invoke([
        {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])
    result = _extract_json(str(response.content))
    return {
        "title": str(result.get("title") or "AI 面试题"),
        "prompt": str(result.get("prompt") or "请结合你的项目经验回答这个问题。"),
        "followUps": result.get("followUps") if isinstance(result.get("followUps"), list) else [],
        "hint": str(result.get("hint") or "建议按背景、方案、取舍、结果组织答案。"),
        "evaluationFocus": result.get("evaluationFocus") if isinstance(result.get("evaluationFocus"), list) else [],
    }


@tool
def generate_report(
    position: str,
    tech_stack: str,
    interview_type: str,
    question_title: str,
    question_prompt: str,
    answer_note: str,
    duration: int = 0,
) -> dict[str, Any]:
    """根据面试会话上下文和作答笔记生成中文复盘报告。

    Args:
        position: 面试岗位
        tech_stack: 技术栈
        interview_type: 面试类型
        question_title: 问题标题
        question_prompt: 问题描述
        answer_note: 候选人的作答笔记
        duration: 答题用时（秒）

    Returns:
        包含 total、question、strengths、weakness、suggestion、nextQuestions 的报告字典
    """
    llm = _create_llm(temperature=DEEPSEEK_TEMPERATURE_REPORT)
    user_prompt = REPORT_USER_TEMPLATE.format(
        position=position or "前端开发实习生",
        tech_stack=tech_stack or "Vue3、JavaScript、CSS、HTTP",
        interview_type=interview_type or "技术面试",
        question_title=question_title or "未提供标题",
        question_prompt=question_prompt or "",
        answer_note=answer_note or "候选人未填写作答笔记",
        duration=duration,
    )
    response = llm.invoke([
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])
    result = _extract_json(str(response.content))
    return {
        "total": int(result.get("total") or 75),
        "question": str(result.get("question") or question_title or "本次模拟面试"),
        "strengths": str(result.get("strengths") or "能够围绕题目展开回答。"),
        "weakness": str(result.get("weakness") or "回答结构还可以更完整。"),
        "suggestion": str(result.get("suggestion") or "建议补充项目案例和关键概念。"),
        "nextQuestions": result.get("nextQuestions") if isinstance(result.get("nextQuestions"), list) else [],
    }
