# AI-Powered Sports Engagement Content Agent

Built for the StapuBox AI Product/Engineer Intern assignment.

Generates 5 types of Instagram-ready sports engagement content — MCQ,
True/False, This-or-That Poll, Fill-in-the-Blank, and Guess-the-Number —
grounded in retrieved facts, validated against a per-type schema, and
served through a Streamlit dashboard.

## Project overview

Content creators need more than repetitive MCQ quizzes to keep followers
engaged. This agent lets a creator pick a sport, difficulty, and one or more
content types, then generates a batch of 4–5 ready-to-post items, each
individually regenerable, each grounded in retrieved facts rather than
LLM guesswork (except This-or-That polls, which are opinion-based by design).

## Type-specific architecture

Rather than one generic prompt, each content type has its own:
1. **Prompt template** (`app/templates.py`) — tailored instructions and
   JSON shape per type.
2. **Schema + validator** (`app/schemas.py`) — a dataclass per type with a
   `.validate()` that enforces the assignment's structural rules (e.g. MCQ
   needs exactly 4 options + 1 correct answer that matches one of them;
   Poll needs exactly 2 options and is flagged opinion-based; Fill-blank
   sentence must contain a `____` blank).
3. Every generated item is retried up to twice if it fails validation.

## Retrieval / grounding strategy

Two complementary retrieval paths feed each prompt as context:

| Source | Used for | File |
|---|---|---|
| Web search (DuckDuckGo, no API key) | fresh/fast-changing facts — recent results, transfers, current form | `app/web_search.py` |
| ChromaDB (local vector DB) | stable/historical facts — records, past tournament winners, career stats | `app/vector_store.py` + `app/seed_facts.py` |

Both are merged into the prompt context, and every generated item is
tagged with a `source` field (`"web search"`, `"vector DB"`,
`"web search + vector DB"`, or `"opinion-based (not fact-checked)"` for
polls) so the origin of every factual claim is traceable — this satisfies
the "cite which source supported each answer" requirement.

This-or-That polls skip retrieval entirely since they're intentionally
subjective.

## Freshness / anti-repetition

`ContentAgent` (`app/agent.py`) keeps an in-memory set of questions
already generated in the current session. On regeneration it nudges the
LLM to avoid repeating a question it's already produced.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"   # console.anthropic.com
streamlit run app.py
```

First run downloads a small local embedding model for ChromaDB
(~90MB, one-time, requires internet).

## Project structure

```
app.py                  # Streamlit dashboard (entry point)
app/
  agent.py              # Orchestrates retrieval -> prompt -> LLM -> validation
  templates.py           # Type-specific prompt templates
  schemas.py             # Type-specific dataclasses + validators
  web_search.py           # Fresh-fact retrieval (DuckDuckGo)
  vector_store.py         # Stable-fact retrieval (ChromaDB)
  seed_facts.py            # Seed data for the vector DB
  llm_client.py            # Claude API wrapper
requirements.txt
```

## Possible next steps (not implemented due to time)

- Persist generated content across sessions (currently in-memory) to
  de-dupe freshness across days, not just within a session.
- Expand the seed fact set / auto-ingest verified web results into
  ChromaDB over time.
- Instagram Quiz/Poll sticker API export format.
