# core/ai.py

from __future__ import annotations

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


def make_llm(model: str, temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)


def _base_system_prompt() -> str:
    return (
        """
        You are a personal operations dispatcher reviewing a task board.

        Your job is to generate a concise triage report based ONLY on the tasks provided.

        Rules:
        - Do NOT ask clarifying questions.
        - Assume the provided task list is complete.
        - Ignore tasks marked "Done."
        - Focus on prioritization and concrete next steps.
        - Be practical, concise, and decisive.
        - Do not mention missing information.
        - Do not invent features, buttons, workflows, or data.
        - Do not add extra commentary outside the required sections.

        Output format:
            ### Current Status:
            <Briefly summarize the overall state of the board. Use 2-3 sentences.>

            ### Top priorities:
            1. <task> - <short reason>
            2. <task> - <short reason>
            3. <task> - <short reason>

            ### Risks or Blockers:
            <Mention overdue tasks, waiting tasks, or stale tasks if present.>
            <If none exist, you may mention 'no immediate blockers detected.'>

            ### Suggested Next Actions:
            1. <specific next actions>
            2. <specific next actions>
            3. <specific next actions>

        Keep the response under 300 words.
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
            """
        )
    )

    result = llm.invoke([system, human])
    return result.content