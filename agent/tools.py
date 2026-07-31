"""
Tool registry for the agent.

Each tool is a plain Python function registered in TOOLS with a name,
description, and callable. The agent core reads this registry to build
the system prompt and to dispatch tool calls it decides to make.

Design note: tools are intentionally simple, dependency-light functions
so the whole project can be understood end-to-end by a reader (and by
you, in an interview) without hidden framework magic.
"""

from __future__ import annotations
import ast
import operator
import datetime as _dt
from typing import Callable, Dict


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def web_search(query: str) -> str:
    """Search the web and return a short summary of the top results."""
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # older package name
        except ImportError:
            return "Error: web search package not installed. Run: pip install ddgs"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return f"No results found for '{query}'."
        lines = []
        for r in results:
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "").strip()
            lines.append(f"- {title}: {body} ({href})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error performing web search: {e}"


def wikipedia_lookup(topic: str) -> str:
    """Look up a topic on Wikipedia and return a short summary."""
    try:
        import wikipedia
    except ImportError:
        return "Error: wikipedia package not installed. Run: pip install wikipedia"

    try:
        summary = wikipedia.summary(topic, sentences=4, auto_suggest=True)
        return summary
    except Exception as e:
        return f"Error looking up '{topic}' on Wikipedia: {e}"


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def _safe_eval(node):
    """Evaluate a restricted arithmetic AST node. No names, no calls, no attrs."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed.")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported or unsafe expression.")


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression, e.g. '(3 + 5) * 12 / 2'."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e}"


def current_datetime(_: str = "") -> str:
    """Return the current date and time (UTC)."""
    return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


# ---------------------------------------------------------------------------
# Registry: name -> (description, function)
# ---------------------------------------------------------------------------

TOOLS: Dict[str, Dict[str, Callable | str]] = {
    "web_search": {
        "description": "Search the web for current information. Input: a search query string.",
        "func": web_search,
    },
    "wikipedia_lookup": {
        "description": "Get a factual summary of a topic from Wikipedia. Input: a topic name.",
        "func": wikipedia_lookup,
    },
    "calculator": {
        "description": "Evaluate an arithmetic expression. Input: a math expression string, e.g. '12 * (3 + 4)'.",
        "func": calculator,
    },
    "current_datetime": {
        "description": "Get the current UTC date and time. Input: ignored, pass an empty string.",
        "func": current_datetime,
    },
}


def run_tool(name: str, tool_input: str) -> str:
    """Dispatch a tool call by name. Returns an observation string."""
    if name not in TOOLS:
        available = ", ".join(TOOLS.keys())
        return f"Error: unknown tool '{name}'. Available tools: {available}"
    try:
        return str(TOOLS[name]["func"](tool_input))  # type: ignore[operator]
    except Exception as e:
        return f"Error running tool '{name}': {e}"
