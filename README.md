# Agentic Task Assistant

A tool-using AI agent built from scratch on the **ReAct pattern** (Reason + Act — Yao et al., 2022). Unlike a single-turn chatbot, this agent plans, decides when it needs external information, calls the right tool, reads the result, and iterates until it can answer confidently — with the full reasoning trace visible in the UI.

By default it runs on **Groq's free API** (Llama 3.3 70B, no credit card required), so you can run the whole project at zero cost. It also supports the Claude API as an optional paid provider — switch between them from the sidebar (`Model provider: Groq (free) / Anthropic (paid)`), or by passing `provider="groq"` / `provider="anthropic"` to `Agent(...)` directly.

**[Live demo](#) — add your deployed Hugging Face Spaces / Render link here**

![screenshot](docs/screenshot.png) <!-- replace with an actual screenshot after you run it -->

## Why this exists

Most fresher "AI chatbot" projects are a thin wrapper around one API call. This project demonstrates:
- Understanding of **agentic loops** (Thought → Action → Observation → ... → Final Answer), implemented without hiding the mechanics behind a heavyweight framework
- **Tool use / function calling** design: a small, safe, extensible tool registry (web search, Wikipedia, a sandboxed calculator, datetime)
- **Production concerns**: bounded step count (cost/runaway protection), error handling when a tool fails, and a step limit fallback
- **Evaluation discipline**: a benchmark suite (`eval/`) that scores the agent on tool-selection correctness, latency, and token cost — not just vibes

## Architecture

```
User task
   │
   ▼
┌─────────────────────────────┐
│  Agent (ReAct loop, core.py)│
│  - builds system prompt     │
│  - calls Groq or Claude API │
│  - parses Thought/Action    │
└──────────────┬──────────────┘
               │ Action + Action Input
               ▼
      ┌────────────────┐
      │  Tool Registry  │  web_search · wikipedia_lookup · calculator · current_datetime
      └────────┬────────┘
               │ Observation
               ▼
      back into the loop, up to MAX_STEPS
               │
               ▼
         Final Answer + trace
```

## Project structure

```
agentic-task-assistant/
├── app.py                 # Streamlit UI - shows live reasoning trace
├── agent/
│   ├── core.py             # ReAct loop + response parser
│   ├── tools.py             # Tool registry (search, wiki, calculator, datetime)
│   └── prompts.py           # System prompt construction
├── eval/
│   ├── test_tasks.json      # Benchmark tasks (tool-use + no-tool-needed cases)
│   └── run_eval.py          # Runs the benchmark, logs tokens/latency/tool choice
├── requirements.txt
└── .env.example
```

## Setup (local, macOS)

```bash
git clone https://github.com/<your-username>/agentic-task-assistant.git
cd agentic-task-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your Groq API key into .env
streamlit run app.py
```

### Getting a free API key (Groq, default)

1. Go to [console.groq.com](https://console.groq.com/keys) and sign up (no credit card).
2. Create an API key (starts with `gsk_...`).
3. Paste it into `.env` as `GROQ_API_KEY=...`, or paste it directly into the sidebar when the app is running.

The app defaults to `provider="groq"` with model `llama-3.3-70b-versatile`, which is on Groq's free tier (rate-limited, but generous enough for this project — see [Groq's docs](https://console.groq.com/docs/rate-limits) for current limits).

### Using Anthropic's Claude API instead (paid)

Claude tends to follow the ReAct output format a bit more reliably and reasons a little more carefully, if you want to compare. It's pay-as-you-go with no ongoing free tier:

1. Get a key at [console.anthropic.com](https://console.anthropic.com/settings/keys) and add billing.
2. In the app sidebar, switch **Model provider** to "Anthropic (paid)" and paste the key (starts with `sk-ant-...`).
3. Or in code: `Agent(api_key="sk-ant-...", provider="anthropic")`.

## Running the evaluation suite

```bash
export GROQ_API_KEY=gsk_...
python eval/run_eval.py
```

Pass `--provider anthropic` (with `ANTHROPIC_API_KEY` set) to benchmark against Claude instead, if `run_eval.py` supports it in your copy — check `eval/run_eval.py` for its current CLI flags.

This runs 6 benchmark tasks (arithmetic, factual lookup, live-web-info, a no-tool-needed reasoning case, and a multi-step tool-chaining case) and reports per-task tool selection, latency, and token cost, plus run-level totals. Results are saved to `eval/results.json`.

## Deployment

Deployed on [Hugging Face Spaces](https://huggingface.co/spaces) (free tier, Streamlit SDK). To deploy your own copy:
1. Create a new Space, SDK = Streamlit
2. Push this repo to the Space's git remote
3. Add `ANTHROPIC_API_KEY` as a Space secret (Settings → Repository secrets)

## Design decisions worth knowing for an interview

- **Why ReAct from scratch instead of LangGraph/CrewAI?** To be able to explain every line of the control flow, not just "the framework did it." A framework choice is easy to add later once the fundamentals are demonstrated.
- **Why a hard step limit?** Agent loops can run away in cost and time if the model gets stuck; `MAX_STEPS` bounds both, and the fallback path still returns the best partial reasoning instead of failing silently.
- **Why a sandboxed calculator instead of `eval()`?** Arbitrary `eval()` on model-controlled input is a code-execution vulnerability; the AST-restricted evaluator only allows numeric literals and arithmetic operators.

## Possible extensions

- Add a code-execution tool (sandboxed) for data-analysis tasks
- Swap the calculator/wiki tools for a domain-specific tool set (e.g. resume screening, expense categorization)
- Add conversation memory across multiple tasks in one session
- Add a cost dashboard aggregating `eval/results.json` over time
