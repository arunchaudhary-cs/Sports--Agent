"""
templates.py
------------
One dedicated prompt template per content type (per assignment requirement:
"Apply a type-specific generation template for each content type ... rather
than one generic prompt for everything").

Every template forces strict JSON output so the response can be parsed and
run through schemas.py validation.
"""

BASE_RULES = """You are a sports content generator for Instagram engagement posts.
Sport: {sport}
Difficulty: {difficulty}
Use ONLY the CONTEXT below to ground every factual claim. If the context is
insufficient, say so in the explanation rather than inventing facts.

CONTEXT:
{context}

Respond with ONLY valid JSON. No markdown, no commentary, no code fences.
"""

MCQ_TEMPLATE = BASE_RULES + """
Generate ONE multiple-choice sports trivia question.
JSON shape:
{{
  "sport": "{sport}",
  "difficulty": "{difficulty}",
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answer": "must exactly match one of the 4 options",
  "explanation": "1-2 sentences, cite the fact"
}}
"""

TRUE_FALSE_TEMPLATE = BASE_RULES + """
Generate ONE true/false sports statement.
JSON shape:
{{
  "sport": "{sport}",
  "difficulty": "{difficulty}",
  "statement": "...",
  "correct_answer": true or false (boolean, not string),
  "explanation": "1-2 sentences, cite the fact"
}}
"""

POLL_TEMPLATE = """You are a sports content generator for Instagram engagement polls.
Sport: {sport}
This is a THIS-OR-THAT poll: pure opinion/engagement bait, NOT a factual question.
Do not fact-check this — it has no correct answer by design.

Respond with ONLY valid JSON, no markdown, no commentary:
{{
  "sport": "{sport}",
  "prompt": "e.g. Messi or Ronaldo - who's the greater dribbler?",
  "options": ["option A", "option B"],
  "is_opinion_based": true
}}
"""

FILL_BLANK_TEMPLATE = BASE_RULES + """
Generate ONE fill-in-the-blank sports sentence with exactly one blank
written as "____".
JSON shape:
{{
  "sport": "{sport}",
  "difficulty": "{difficulty}",
  "sentence": "In 2011, India won the Cricket World Cup held in ____.",
  "options": ["...", "...", "...", "..."],
  "correct_answer": "must exactly match one of the 4 options",
  "explanation": "1-2 sentences, cite the fact"
}}
"""

GUESS_NUMBER_TEMPLATE = BASE_RULES + """
Generate ONE "guess the number" sports question with a numeric answer.
JSON shape:
{{
  "sport": "{sport}",
  "difficulty": "{difficulty}",
  "question": "e.g. How many runs did Virat Kohli score in the 2023 World Cup?",
  "target_number": 765,
  "tolerance": 5,
  "explanation": "1-2 sentences, cite the fact"
}}
"""

TEMPLATE_MAP = {
    "mcq": MCQ_TEMPLATE,
    "true_false": TRUE_FALSE_TEMPLATE,
    "this_or_that": POLL_TEMPLATE,
    "fill_blank": FILL_BLANK_TEMPLATE,
    "guess_number": GUESS_NUMBER_TEMPLATE,
}


def build_prompt(content_type: str, sport: str, difficulty: str, context: str) -> str:
    tpl = TEMPLATE_MAP[content_type]
    if content_type == "this_or_that":
        return tpl.format(sport=sport)
    return tpl.format(sport=sport, difficulty=difficulty, context=context or "No extra context retrieved.")
