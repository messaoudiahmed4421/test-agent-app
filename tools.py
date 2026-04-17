"""Single-tool module used by the ADK agent."""

from datetime import datetime


def generate_report(topic: str, ai_draft: str) -> str:
    """Format and return the final report produced by the LLM draft."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    safe_topic = (topic or "General request").strip()
    safe_draft = (ai_draft or "").strip()
    if not safe_draft:
        safe_draft = "No draft content was provided by the model."

    return (
        "## AI Generated Report\n"
        f"Topic: {safe_topic}\n"
        f"Generated: {timestamp}\n\n"
        f"{safe_draft}\n"
    )

