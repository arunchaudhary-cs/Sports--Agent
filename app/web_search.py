"""
web_search.py
-------------
Fetches recent/fast-changing sports info (scores, transfers, tournament
results) so the LLM is grounded in fresh facts instead of hallucinating.

Uses the `ddgs` (DuckDuckGo Search) package — free, no API key required,
which matters since this needs to work with zero setup/credentials.
If you have a Tavily/SerpAPI key, swap the implementation below; the
rest of the app only depends on `search_web()`'s return shape.
"""

from typing import List, Dict

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


def search_web(query: str, max_results: int = 4) -> List[Dict]:
    """
    Returns a list of {"title", "snippet", "url"} dicts.
    Falls back to an empty list (never crashes the app) if the search
    library isn't installed or the network call fails — the agent will
    then rely on ChromaDB context only, and the LLM is instructed to
    flag when context is insufficient rather than invent facts.
    """
    if DDGS is None:
        return []
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                })
        return results
    except Exception:
        return []


def format_context(results: List[Dict]) -> str:
    if not results:
        return ""
    lines = []
    for r in results:
        lines.append(f"- {r['title']}: {r['snippet']} (source: {r['url']})")
    return "\n".join(lines)
