# core/ai.py

from __future__ import annotations

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


def make_llm(model: str, temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)


def _base_system_prompt() -> str:
    return (
        """
        You are a personal operations dispatcher reviewing a personal task board.

        Your goal is to produce a concise triage summary that helps the user decide what to work on next today.

        You will receive structured task data including status, priority, due dates, and other metadata.

        Guidelines:
        - Use metadata only for internal reasoning.
        - Do NOT expose metadata fields in the output.
        - Never copy raw task lines or field-value pairs into the response.
        - Do not repeat strings like: status=..., priority=..., queue=..., due=..., stale_days=..., urgency_score=...
        - Convert structured task data into natural human language.
        - Rewrite task titles naturally when helpful, but preserve their meaning.

        Rules:
        - Do NOT ask clarifying questions.
        - Assume the provided task list is complete.
        - Ignore tasks marked Done.
        - Focus on prioritization and concrete next steps.
        - Be practical, concise, and decisive.
        - Do not mention missing information.
        - Do not invent features, buttons, workflows, or data.
        - Do not invent tasks, deadlines, or blockers.
        - Only mention tasks that appear in the provided context.
        - Do not add extra commentary outside the required sections.

        Output format:
        # Triage Report

        ### Current Status:
        <Briefly summarize the overall state of the board in 1-2 sentences.>

        ### Top priorities:
        1. <natural task summary> - <short human-readable reason>
        2. <natural task summary> - <short human-readable reason>
        3. <natural task summary> - <short human-readable reason>

        ### Risks or Blockers:
        - Mention overdue tasks, waiting tasks, or stale tasks if present.
        - If none exist, write exactly: No immediate blockers detected.

        ### Suggested Next Actions:
        1. <specific next action>
        2. <specific next action>
        3. <specific next action>

        Keep the response under 180 words.
        """
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
            f"""
            TASK BOARD CONTEXT:\n{context}\n\n
            Generate the triage report now.
            Use natural language and do not expose metadata.
            """
        )
    )

    result = llm.invoke([system, human])
    return result.content