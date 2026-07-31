"""
Streamlit UI for the Agentic Task Assistant.

Shows the agent's live Thought -> Action -> Observation trace, not just the
final answer, so a viewer (or a recruiter) can see the reasoning process.
"""

import os
import streamlit as st
from agent.core import Agent
from agent.tools import TOOLS

st.set_page_config(page_title="Agentic Task Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Agentic Task Assistant")
st.caption(
    "A from-scratch ReAct agent (Thought → Action → Observation) built on the Claude API. "
    "Ask it something that needs a real tool - live info, a calculation, a lookup."
)

with st.sidebar:
    st.header("Available tools")
    for name, meta in TOOLS.items():
        st.markdown(f"**{name}**")
        st.caption(meta["description"])
    st.divider()
    provider_label = st.radio(
        "Model provider",
        ["Groq (free)", "Anthropic (paid)"],
        help=(
            "Groq's API has a free tier (no credit card) and runs Llama 3.3 70B. "
            "Anthropic's Claude API is pay-as-you-go, no ongoing free tier."
        ),
    )
    provider = "groq" if provider_label.startswith("Groq") else "anthropic"

    if provider == "groq":
        key_env = "GROQ_API_KEY"
        key_label = "Groq API key"
        key_help = "Free at console.groq.com — no credit card required. Stored only in this session, never logged."
    else:
        key_env = "ANTHROPIC_API_KEY"
        key_label = "Anthropic API key"
        key_help = "Pay-as-you-go at console.anthropic.com. Stored only in this session, never logged."

    api_key = st.text_input(
        key_label,
        type="password",
        value=os.environ.get(key_env, ""),
        help=key_help,
    )
    st.divider()
    st.markdown("**Try:**")
    examples = [
        "What's 15% of the sum of 340 and 860?",
        "Who is the current CEO of Anthropic, and give me one fact about them?",
        "What year did the James Webb Space Telescope launch, and how many years after Hubble was that?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["task_input"] = ex

task = st.text_area("Task", key="task_input", height=100, placeholder="Ask the agent to do something...")
run_clicked = st.button("Run agent", type="primary")

if run_clicked:
    if not api_key:
        st.error(f"Please enter your {key_label} in the sidebar.")
    elif not task.strip():
        st.warning("Please enter a task.")
    else:
        agent = Agent(api_key=api_key, provider=provider)
        trace_container = st.container()
        step_num = {"n": 0}

        def render_step(step):
            step_num["n"] += 1
            with trace_container.expander(f"Step {step_num['n']}", expanded=True):
                st.markdown(f"**Thought:** {step.thought}")
                if step.action:
                    st.markdown(f"**Action:** `{step.action}`")
                    st.markdown(f"**Action Input:** {step.action_input}")
                if step.observation:
                    st.markdown("**Observation:**")
                    st.code(step.observation, language=None)
                if step.final_answer:
                    st.markdown(f"**Final Answer:** {step.final_answer}")

        with st.spinner("Agent working..."):
            result = agent.run(task, on_step=render_step)

        st.divider()
        st.subheader("Answer")
        st.success(result.answer)

        cols = st.columns(4)
        cols[0].metric("Steps taken", len(result.steps))
        cols[1].metric("Input tokens", result.input_tokens)
        cols[2].metric("Output tokens", result.output_tokens)
        cols[3].metric("Latency (s)", f"{result.latency_seconds:.1f}")

        if result.hit_step_limit:
            st.warning("Agent hit its step limit before reaching a confident final answer.")
