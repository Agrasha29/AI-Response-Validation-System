from typing import Literal
from pydantic import BaseModel, Field

from src.llm_client import generate_structured


class RelevanceResult(BaseModel):

    relevance_score: Literal["1", "2", "3", "4", "5"] = Field(
        description="Relevance score: 1=Completely irrelevant, "
                    "2=Mostly irrelevant, "
                    "3=Partially relevant, "
                    "4=Mostly relevant, "
                    "5=Fully relevant."
    )

    reasoning: str = Field(
        description="Clear explanation for the relevance score."
    )


def evaluate_relevance(
    question: str,
    response: str
) -> RelevanceResult:

    prompt = f"""
You are a professional LLM response relevance evaluator.

Evaluate ONLY how relevant the AI response is to the question.

Do NOT evaluate factual correctness.
Do NOT evaluate hallucination.

Scoring:

1 = Completely irrelevant
2 = Mostly irrelevant
3 = Partially relevant
4 = Mostly relevant
5 = Fully relevant

Question:
{question}

AI Response:
{response}

Return the appropriate score and explain your reasoning.
"""

    return generate_structured(
        prompt,
        RelevanceResult
    )