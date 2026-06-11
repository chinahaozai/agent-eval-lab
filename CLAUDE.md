# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A from-scratch, minimal **Agent Evaluation (Eval)** project, built as a job-portfolio piece. The end state: a tool-using agent → trajectory logging → three classes of evaluation → a web trajectory replayer. It is built **day by day** against a fixed roadmap in `PLAN.md` — read `PLAN.md` before adding features so work lands in the right phase. As of the latest commit only **Day 1** (first API call) exists.

Each day has an explicit **完成标志 (completion marker)** in `PLAN.md`. Don't skip ahead past an unmet marker — the project deliberately gates each step on a verifiable outcome.

## Commands

```bash
# Setup (uv preferred)
uv venv --python 3.12 && source .venv/bin/activate && uv pip install -r requirements.txt

# Configure a provider (required before running anything that calls the LLM)
cp .env.example .env   # then fill LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

# Run a module (the project runs modules, not scripts — note the -m and src. prefix)
python -m src.hello_llm
```

There is no test runner or linter configured yet (deps are intentionally minimal: `openai`, `python-dotenv`). Add them per the relevant PLAN.md week rather than pulling them in early.

## Architecture

**`src/config.py` is the single provider-abstraction layer** and the most important file to understand. Everything that touches the LLM goes through it:

- `get_client() -> (OpenAI, Settings)` is the canonical entry point — other modules call this, never construct a client themselves.
- All four supported providers (DeepSeek / Qwen / OpenAI / Claude) are reached through the **OpenAI-compatible interface**, so switching provider is a `.env` change only — business code never changes. This is deliberate: cross-model comparison is core to the eval work, so the provider must be swappable from day one.
- `load_settings()` reads the three required env vars and **exits with a Chinese error message if any is missing** — that exit is expected behavior, not a bug.
- `estimate_cost(model, prompt_tokens, completion_tokens)` uses the `PRICE_PER_1M_TOKENS` table; unregistered models estimate to 0. Input prices are recorded at the **cache-miss (upper-bound)** rate; precise cache-aware accounting is deferred to the eval-metrics week.
- `REQUEST_TIMEOUT_SECONDS` (60s) is applied to every client; external calls must always have a timeout.

`data/` holds trajectory JSONL output (git-ignored; `data/*.jsonl`). The trajectory schema and JSONL persistence are a Week-1 deliverable (Days 5–6) — not built yet.

## Hard rules

- **Never introduce LangChain (or any agent framework).** This is the project's iron rule. The whole point is an Eval that can see exactly how each trajectory step is produced; a framework turns that into a black box. The agent loop must be hand-written (Day 3).
- **Match the existing language convention:** all comments, docstrings, prompts, and docs are in **Chinese**. New code should follow suit.
