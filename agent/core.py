"""
Core ReAct agent loop.

Implements the classic Reason + Act pattern from scratch (Yao et al., 2022,
"ReAct: Synergizing Reasoning and Acting in Language Models") on top of an
LLM API, so the mechanics are fully visible rather than hidden inside a
framework. Each step is one of:

  Thought -> Action -> Action Input   (agent wants to use a tool)
  Thought -> Final Answer             (agent is done)

The loop feeds tool Observations back to the model until it reaches a
Final Answer or hits a step limit (to guarantee termination and bound cost).

Because the loop only ever sends a system prompt + a plain-text transcript
(no provider-specific tool-calling schema), the model call is a thin,
swappable seam. Two providers are supported out of the box:

  - "groq"      (default): Groq's OpenAI-compatible endpoint. Free tier,
                 no credit card required. Runs open-weight models
                 (Llama 3.3 70B by default) at very high tokens/sec.
  - "anthropic": The real Claude API. Higher quality, but pay-as-you-go
                 with no ongoing free tier.
"""

from __future__ import annotations
import os
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional

from agent.tools import TOOLS, run_tool
from agent.prompts import build_system_prompt

MAX_STEPS = 6

# Default model per provider.
DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "anthropic": "claude-sonnet-4-6",
}

# Env var each provider's key is conventionally read from.
ENV_KEY_NAMES = {
    "groq": "GROQ_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


@dataclass
class Step:
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    final_answer: Optional[str] = None


@dataclass
class AgentResult:
    answer: str
    steps: List[Step] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_seconds: float = 0.0
    hit_step_limit: bool = False


_THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|\Z)", re.S)
_ACTION_RE = re.compile(r"Action:\s*(.*?)\n", re.S)
_ACTION_INPUT_RE = re.compile(r"Action Input:\s*(.*?)\Z", re.S)
_FINAL_RE = re.compile(r"Final Answer:\s*(.*?)\Z", re.S)


def _parse(text: str) -> Step:
    thought_match = _THOUGHT_RE.search(text)
    thought = thought_match.group(1).strip() if thought_match else ""

    final_match = _FINAL_RE.search(text)
    if final_match:
        return Step(thought=thought, final_answer=final_match.group(1).strip())

    action_match = _ACTION_RE.search(text)
    input_match = _ACTION_INPUT_RE.search(text)
    action = action_match.group(1).strip() if action_match else None
    action_input = input_match.group(1).strip() if input_match else ""

    return Step(thought=thought, action=action, action_input=action_input)


class Agent:
    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "groq",
        model: Optional[str] = None,
        max_steps: int = MAX_STEPS,
    ):
        if provider not in DEFAULT_MODELS:
            raise ValueError(f"Unknown provider '{provider}'. Use 'groq' or 'anthropic'.")

        self.provider = provider
        self.model = model or DEFAULT_MODELS[provider]
        self.max_steps = max_steps
        self.system_prompt = build_system_prompt(TOOLS)

        resolved_key = api_key or os.environ.get(ENV_KEY_NAMES[provider])
        if not resolved_key:
            raise ValueError(
                f"No API key provided for provider '{provider}'. "
                f"Pass api_key= or set {ENV_KEY_NAMES[provider]}."
            )

        if provider == "groq":
            # Groq exposes an OpenAI-compatible /v1 endpoint, so the official
            # `openai` SDK works unchanged - just point base_url at Groq.
            from openai import OpenAI

            self.client = OpenAI(api_key=resolved_key, base_url="https://api.groq.com/openai/v1")
        else:
            import anthropic

            self.client = anthropic.Anthropic(api_key=resolved_key)

    def _call_model(self, transcript: str):
        """Send the transcript to the configured provider. Returns
        (response_text, input_tokens, output_tokens)."""
        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": transcript},
                ],
            )
            text = response.choices[0].message.content or ""
            usage = response.usage
            return text, usage.prompt_tokens, usage.completion_tokens
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": transcript}],
            )
            text = "".join(block.text for block in response.content if block.type == "text")
            return text, response.usage.input_tokens, response.usage.output_tokens

    def run(self, task: str, on_step=None) -> AgentResult:
        """Run the agent on a task. `on_step` is an optional callback(Step) for
        streaming the trace to a UI as each step completes."""
        start = time.time()
        transcript = f"Task: {task}\n"
        steps: List[Step] = []
        total_in, total_out = 0, 0

        for _ in range(self.max_steps):
            text, in_tokens, out_tokens = self._call_model(transcript)
            total_in += in_tokens
            total_out += out_tokens

            step = _parse(text)
            steps.append(step)
            if on_step:
                on_step(step)

            if step.final_answer is not None:
                return AgentResult(
                    answer=step.final_answer,
                    steps=steps,
                    input_tokens=total_in,
                    output_tokens=total_out,
                    latency_seconds=time.time() - start,
                )

            if step.action:
                observation = run_tool(step.action, step.action_input or "")
                step.observation = observation
                transcript += (
                    f"Thought: {step.thought}\n"
                    f"Action: {step.action}\n"
                    f"Action Input: {step.action_input}\n"
                    f"Observation: {observation}\n"
                )
            else:
                # Model produced neither a valid action nor a final answer.
                # Nudge it back on format rather than silently failing.
                transcript += (
                    f"Thought: {step.thought}\n"
                    "Observation: Your last response didn't match the required format. "
                    "Respond with either Action/Action Input or Final Answer.\n"
                )

        # Step limit reached without a final answer.
        fallback = steps[-1].thought if steps else "Unable to complete the task in time."
        return AgentResult(
            answer=f"[Stopped after {self.max_steps} steps] Best attempt: {fallback}",
            steps=steps,
            input_tokens=total_in,
            output_tokens=total_out,
            latency_seconds=time.time() - start,
            hit_step_limit=True,
        )
