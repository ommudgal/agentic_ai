from pydantic import BaseModel
from enum import Enum


class QuestionType(str, Enum):
    mcq = "mcq"
    integer = "integer"


class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QueryInput(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    type: QuestionType
    number: int


class MCQQuestion(BaseModel):
    question: str
    option_A: str
    option_B: str
    option_C: str
    option_D: str
    answer: str


class IntegerTypeQuestion(BaseModel):
    question: str
    answer: float
