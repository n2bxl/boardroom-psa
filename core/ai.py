# core/ai.py
from __future__ import annotations

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


def make_llm(model: str, temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)


def _base_system_prompt() -> str:
    return (
        "You are a practical personal service-desk triage assistant for a ticketing-style life dashboard.\n"
        "Rules:\n"
        "- Only reference features, buttons, or data that appear in the provided context.\n"
        "- If something is not explicitly in context, say you are not sure and ask a short clarifying question.\n"
        "- Do not invent UI elements or automations.\n"
        "- Be concise and actionable.\n"
        "- Use the requested output format exactly.\n"
    )


def coach_reply(model: str, user_message: str, context: str, temperature: float = 0.2) -> str:
    llm = make_llm(model=model, temperature=temperature)

    system = SystemMessage(content=_base_system_prompt())
    human = HumanMessage(
        content=(
            f"CONTEXT:\n{context}\n\n"
            f"USER MESSAGE:\n{user_message}\n\n"
            "Output format:\n"
            "Triage Summary:\n"
            "- ...\n"
            "\n"
            "Top 3 Next Actions:\n"
            "1) ...\n"
            "2) ...\n"
            "3) ...\n"
            "\n"
            "Risks/Blocks:\n"
            "- ...\n"
            "\n"
            "Ask-Back Questions (if needed):\n"
            "- ...\n"
        )
    )

    result = llm.invoke([system, human])
    return result.content


def daily_triage(model: str, context: str) -> str:
    """
    One-click triage report for the Board page.
    """
    llm = make_llm(model=model, temperature=0.1)

    system = SystemMessage(content=_base_system_prompt())
    human = HumanMessage(
        content=(
            f"CONTEXT:\n{context}\n\n"
            "You are running a daily triage for the ticket queue.\n"
            "Prioritize by:\n"
            "1) Overdue\n"
            "2) Due today\n"
            "3) High priority\n"
            "4) Quick wins\n"
            "\n"
            "Output format:\n"
            "Queue Health:\n"
            "- Open: <number if available>\n"
            "- Due Today: <number if available>\n"
            "- Overdue: <number if available>\n"
            "- Waiting: <number if available>\n"
            "\n"
            "Today's Focus (Top 5 Tickets):\n"
            "1) <ticket summary> | recommended status change: <New/In Progress/Waiting/Done/none>\n"
            "2) ...\n"
            "3) ...\n"
            "4) ...\n"
            "5) ...\n"
            "\n"
            "Recommended Next 3 Steps:\n"
            "1) ...\n"
            "2) ...\n"
            "3) ...\n"
            "\n"
            "If you need more info, ask up to 2 questions.\n"
        )
    )

    result = llm.invoke([system, human])
    return result.content