"""
schemas.py
----------
Defines the expected shape of each of the 5 content types and validates
every item the LLM produces before it is shown to the user.

Why manual validation instead of trusting the LLM:
The assignment explicitly requires "Validate every generated item against
a schema for its type before returning it". LLMs occasionally drop a field
or return 3 options instead of 4, so every item is checked here and
rejected/regenerated if it fails.
"""

from dataclasses import dataclass, field
from typing import List, Optional


class SchemaValidationError(Exception):
    pass


@dataclass
class MCQItem:
    sport: str
    difficulty: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    source: str = "unknown"
    type: str = "mcq"

    def validate(self):
        if len(self.options) != 4:
            raise SchemaValidationError("MCQ must have exactly 4 options")
        if self.correct_answer not in self.options:
            raise SchemaValidationError("MCQ correct_answer must be one of the 4 options")
        if not self.question.strip():
            raise SchemaValidationError("MCQ question cannot be empty")


@dataclass
class TrueFalseItem:
    sport: str
    difficulty: str
    statement: str
    correct_answer: bool
    explanation: str
    source: str = "unknown"
    type: str = "true_false"

    def validate(self):
        if not isinstance(self.correct_answer, bool):
            raise SchemaValidationError("True/False correct_answer must be boolean")
        if not self.statement.strip():
            raise SchemaValidationError("Statement cannot be empty")


@dataclass
class PollItem:
    sport: str
    prompt: str
    options: List[str]
    is_opinion_based: bool = True
    source: str = "opinion-based (not fact-checked)"
    type: str = "this_or_that"

    def validate(self):
        if len(self.options) != 2:
            raise SchemaValidationError("This-or-That poll must have exactly 2 options")
        if not self.is_opinion_based:
            raise SchemaValidationError("Poll must be flagged opinion-based")


@dataclass
class FillBlankItem:
    sport: str
    difficulty: str
    sentence: str  # must contain "____"
    options: List[str]
    correct_answer: str
    explanation: str
    source: str = "unknown"
    type: str = "fill_blank"

    def validate(self):
        if "____" not in self.sentence:
            raise SchemaValidationError("Fill-in-the-blank sentence must contain a '____' blank")
        if len(self.options) != 4:
            raise SchemaValidationError("Fill-in-the-blank must have exactly 4 options")
        if self.correct_answer not in self.options:
            raise SchemaValidationError("correct_answer must be one of the 4 options")


@dataclass
class GuessNumberItem:
    sport: str
    difficulty: str
    question: str
    target_number: float
    tolerance: float
    explanation: str
    source: str = "unknown"
    type: str = "guess_number"

    def validate(self):
        if self.tolerance < 0:
            raise SchemaValidationError("Tolerance cannot be negative")
        if not self.question.strip():
            raise SchemaValidationError("Question cannot be empty")


TYPE_MAP = {
    "mcq": MCQItem,
    "true_false": TrueFalseItem,
    "this_or_that": PollItem,
    "fill_blank": FillBlankItem,
    "guess_number": GuessNumberItem,
}


def build_and_validate(content_type: str, data: dict):
    """Instantiate the right dataclass from raw LLM dict output, validate, return it."""
    cls = TYPE_MAP[content_type]
    # Only keep keys the dataclass accepts
    allowed = cls.__dataclass_fields__.keys()
    clean = {k: v for k, v in data.items() if k in allowed}
    obj = cls(**clean)
    obj.validate()
    return obj
          
