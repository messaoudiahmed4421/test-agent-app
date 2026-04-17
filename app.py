"""Minimal Streamlit app for deployment smoke testing."""

import streamlit as st

from instructions import DEFAULT_REQUEST
from pipeline import run_pipeline

st.set_page_config(page_title="Minimal ADK Deploy Test", page_icon="🚀", layout="centered")

st.title("Minimal ADK Deployment Test")
request_text = st.text_area(
    "Request",
    value=DEFAULT_REQUEST,
    height=100,
    help="This prompt is sent to Gemini through the ADK agent.",
)

if "running" not in st.session_state:
    st.session_state.running = False
if "status" not in st.session_state:
    st.session_state.status = "Idle"
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "result" not in st.session_state:
    st.session_state.result = ""

status_box = st.empty()
progress_box = st.empty()
results_box = st.container(border=True)


def update_progress(value: int, message: str) -> None:
    st.session_state.progress = value
    st.session_state.status = message
    status_box.info(f"Status: {message}")
    progress_box.progress(value)


status_box.info(f"Status: {st.session_state.status}")
progress_box.progress(st.session_state.progress)

if st.button("Run", type="primary", disabled=st.session_state.running, use_container_width=True):
    st.session_state.running = True
    st.session_state.result = ""
    try:
        result = run_pipeline(update_progress, request_text=request_text)
        st.session_state.result = result
        st.session_state.status = "Completed"
        st.session_state.progress = 100
    except Exception as e:
        st.session_state.status = "Failed"
        st.session_state.result = (
            "## Report\n"
            "The pipeline failed before returning an agent response.\n\n"
            "### Details\n"
            f"- Error: {e}"
        )
        status_box.error("Status: Failed")
    finally:
        st.session_state.running = False

status_box.info(f"Status: {st.session_state.status}")
progress_box.progress(st.session_state.progress)

with results_box:
    st.subheader("Results")
    if st.session_state.result:
        st.markdown(st.session_state.result)
    else:
        st.caption("Run the pipeline to see the report.")
