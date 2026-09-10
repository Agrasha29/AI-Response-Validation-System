from typing import Literal
from pydantic import BaseModel, Field

from src.llm_client import generate_structured


class RelevanceResult(BaseModel):
    relevance_score: Literal[1, 2, 3, 4, 5] = Field(
        description="Relevance score from 1 to 5."
    )

    reasoning: str = Field(
        description="Clear explanation for why the response received this score."
    )


def evaluate_relevance(question: str, response: str) -> RelevanceResult:
    """
    Evaluates how directly the AI response answers the question.

    Scoring:
    1 = Completely irrelevant
    2 = Mostly irrelevant
    3 = Partially relevant
    4 = Mostly relevant
    5 = Fully relevant
    """

    prompt = f"""
You are a professional LLM response relevance evaluator.

Your task is to evaluate ONLY the relevance of the AI response
to the user's question.

Do NOT evaluate factual correctness.
Do NOT evaluate hallucination.
Only evaluate whether the response addresses the question.

Scoring criteria:

5 = Fully relevant.
    Directly answers the question and stays focused.

4 = Mostly relevant.
    Answers the question but contains minor unnecessary information.

3 = Partially relevant.
    Addresses some part of the question but misses important aspects.

2 = Mostly irrelevant.
    Has a weak connection to the question but does not properly answer it.

1 = Completely irrelevant.
    Does not address the question.

Question:
{question}

AI Response:
{response}

Return a score and concise reasoning.
"""

    return generate_structured(prompt, RelevanceResult)