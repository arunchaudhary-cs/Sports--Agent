"""
agent.py
--------
The orchestration layer. For each requested item:
 1. Decide retrieval strategy based on content type:
      - This-or-That poll -> no retrieval needed (opinion-based by design)
      - Otherwise -> pull FAST-CHANGING context from web search AND
        STABLE/historical context from ChromaDB, merge them
 2. Build the type-specific prompt (templates.py)
 3. Call the LLM (llm_client.py)
 4. Validate against the schema (schemas.py); retry once on failure
 5. Attach a `source` tag so every item can cite web search / vector DB /
    or "opinion-based" per the grounding requirement

Also tracks recently-generated questions per session (in-memory) so
regeneration avoids repeating the same fact.
"""

import random
from app import web_search, vector_store, templates, schemas, llm_client

MAX_RETRIES = 2


class ContentAgent:
    def __init__(self):
        # simple in-memory de-dup memory for "freshness" within a session
        self.seen_questions = set()

    def _retrieve_context(self, content_type: str, sport: str, difficulty: str):
        if content_type == "this_or_that":
            return "", "opinion-based (not fact-checked)"

        web_results = web_search.search_web(f"{sport} {difficulty} facts records recent news")
        vector_results = vector_store.query_facts(sport)

        web_ctx = web_search.format_context(web_results)
        vector_ctx = vector_store.format_context(vector_results)

        combined = "\n".join(filter(None, [
            "[WEB SEARCH — recent/fast-changing]:\n" + web_ctx if web_ctx else "",
            "[VECTOR DB — stable/historical]:\n" + vector_ctx if vector_ctx else "",
        ]))

        if web_ctx and vector_ctx:
            source = "web search + vector DB"
        elif web_ctx:
            source = "web search"
        elif vector_ctx:
            source = "vector DB"
        else:
            source = "LLM knowledge (no retrieval hits — flagged)"

        return combined, source

    def generate_item(self, content_type: str, sport: str, difficulty: str):
        """Generate ONE validated item. Raises on repeated failure."""
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            context, source = self._retrieve_context(content_type, sport, difficulty)
            prompt = templates.build_prompt(content_type, sport, difficulty, context)

            try:
                raw = llm_client.generate_json(prompt)
                dedup_key = raw.get("question") or raw.get("statement") or raw.get("prompt") or raw.get("sentence")

                # nudge for a different question if we've seen this one this session
                if dedup_key in self.seen_questions and attempt < MAX_RETRIES:
                    continue

                raw["source"] = source
                item = schemas.build_and_validate(content_type, raw)

                if dedup_key:
                    self.seen_questions.add(dedup_key)
                return item
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"Failed to generate valid {content_type} after retries: {last_error}")

    def generate_batch(self, sport: str, difficulty: str, content_types: list, batch_size: int = 5):
        """
        content_types: list of allowed types to mix in this batch, e.g.
        ["mcq", "true_false", "this_or_that", "fill_blank", "guess_number"]
        """
        items = []
        for i in range(batch_size):
            ctype = content_types[i % len(content_types)] if len(content_types) > 1 else content_types[0]
            try:
                items.append(self.generate_item(ctype, sport, difficulty))
            except Exception as e:
                items.append({"error": str(e), "type": ctype})
        return items

