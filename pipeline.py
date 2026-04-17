"""Pipeline orchestration for one-agent, one-tool demo."""

import asyncio
import os
import uuid
from typing import Callable

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents import build_agent
from instructions import DEFAULT_REQUEST


def _resolve_api_key() -> str | None:
    """Resolve API key by loading apikey.env and exporting GOOGLE_API_KEY."""
    # 1) Try to load from local env file, forcing refresh if value changed.
    load_dotenv("apikey.env", override=True)
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # 2) Ensure downstream libraries can read it from process environment.
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key

    return None


async def _run_agent_once(request_text: str) -> str:
    """Run one ADK interaction and return the generated report text."""
    agent = build_agent()
    session_service = InMemorySessionService()
    app_name = "minimal_streamlit_adk_app"
    user_id = "streamlit_user"
    session_id = f"run-{uuid.uuid4().hex[:8]}"

    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    prompt = types.Content(role="user", parts=[types.Part(text=request_text)])

    text_parts: list[str] = []
    tool_parts: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=prompt,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                text = getattr(part, "text", None)
                if text and text.strip():
                    text_parts.append(text.strip())

                function_response = getattr(part, "function_response", None)
                if function_response:
                    response = getattr(function_response, "response", None)
                    if isinstance(response, str) and response.strip():
                        tool_parts.append(response.strip())
                    elif isinstance(response, dict):
                        for key in ("result", "output", "text", "report"):
                            value = response.get(key)
                            if isinstance(value, str) and value.strip():
                                tool_parts.append(value.strip())
                                break

    if tool_parts:
        return tool_parts[-1]

    if text_parts:
        # Prefer the first report-like chunk if present.
        for chunk in reversed(text_parts):
            if "## Report" in chunk or "### Summary" in chunk:
                return chunk
        return text_parts[-1]

    return ""


def run_pipeline(update_progress: Callable[[int, str], None], request_text: str | None = None) -> str:
    """Run pipeline and return final report text."""
    text = (request_text or DEFAULT_REQUEST).strip()

    update_progress(5, "Initializing pipeline")

    api_key = _resolve_api_key()
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY.")

    update_progress(20, "Building ADK agent")

    update_progress(50, "Sending request to Gemini agent")

    update_progress(80, "Running agent and tool")
    try:
        result = asyncio.run(_run_agent_once(text))
    except RuntimeError:
        # Fallback for environments with an active event loop.
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_run_agent_once(text))
        finally:
            loop.close()
    except Exception as e:
        raise RuntimeError(f"Agent execution failed: {e}") from e

    if not result:
        raise RuntimeError("Agent returned empty output.")

    update_progress(100, "Completed")
    return result
