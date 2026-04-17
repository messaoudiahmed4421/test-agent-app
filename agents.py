"""Single LLM agent definition using Google ADK."""

from google.adk.agents import LlmAgent

from instructions import AGENT_INSTRUCTION
from tools import generate_report


def build_agent(model_name: str = "gemini-2.5-flash") -> LlmAgent:
    """Create one ADK LLM agent with exactly one tool."""
    return LlmAgent(
        name="MinimalReportAgent",
        model=model_name,
        instruction=AGENT_INSTRUCTION,
        tools=[generate_report],
    )
