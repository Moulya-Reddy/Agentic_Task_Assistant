"""
Evaluation harness for the agent.

Runs a fixed set of benchmark tasks (eval/test_tasks.json) through the agent
and reports, per task: whether it used the expected tool(s), latency, token
usage, and the final answer for manual correctness review. Results are
written to eval/results.json so runs are comparable over time - this is
the difference between a demo and something you can defend numbers on
in an interview.

Usage:
    export GROQ_API_KEY=gsk_...
    python eval/run_eval.py

    # Or benchmark against Claude instead:
    export ANTHROPIC_API_KEY=sk-ant-...
    python eval/run_eval.py --provider anthropic
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.core import Agent  # noqa: E402

HERE = Path(__file__).resolve().parent


def load_tasks():
    with open(HERE / "test_tasks.json") as f:
        return json.load(f)


ENV_KEY_NAMES = {"groq": "GROQ_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}


def main():
    parser = argparse.ArgumentParser(description="Run the agent eval suite.")
    parser.add_argument(
        "--provider",
        choices=["groq", "anthropic"],
        default="groq",
        help="Which model provider to benchmark (default: groq, free tier).",
    )
    args = parser.parse_args()

    env_key = ENV_KEY_NAMES[args.provider]
    api_key = os.environ.get(env_key)
    if not api_key:
        print(f"Error: set {env_key} before running eval with provider='{args.provider}'.")
        sys.exit(1)

    tasks = load_tasks()
    agent = Agent(api_key=api_key, provider=args.provider)
    results = []

    print(f"Running {len(tasks)} eval tasks...\n")
    for t in tasks:
        print(f"[{t['id']}] {t['task']}")
        result = agent.run(t["task"])

        tools_used = [s.action for s in result.steps if s.action]
        record = {
            "id": t["id"],
            "task": t["task"],
            "expected_tool": t["expects_tool"],
            "tools_used": tools_used,
            "answer": result.answer,
            "steps": len(result.steps),
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "latency_seconds": round(result.latency_seconds, 2),
            "hit_step_limit": result.hit_step_limit,
        }
        results.append(record)

        print(f"  -> tools used: {tools_used or 'none'}")
        print(f"  -> answer: {result.answer[:200]}")
        print(f"  -> {result.input_tokens} in / {result.output_tokens} out tokens, "
              f"{result.latency_seconds:.1f}s, {len(result.steps)} steps\n")

    out_path = HERE / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    total_in = sum(r["input_tokens"] for r in results)
    total_out = sum(r["output_tokens"] for r in results)
    avg_latency = sum(r["latency_seconds"] for r in results) / len(results)

    print("=" * 60)
    print(f"Total tokens: {total_in} in / {total_out} out")
    print(f"Average latency: {avg_latency:.1f}s per task")
    print(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
