from typing import Literal
from pydantic import BaseModel, Field

from src.llm_client import generate_structured


class AccuracyResult(BaseModel):
    accuracy_score: Literal[1, 2, 3, 4, 5] = Field(
        description="Accuracy score from 1 to 5."
    )

    reasoning: str = Field(
        description="Explanation of the factual correctness of the response."
    )

    evidence: str = Field(
        description="Reference evidence supporting the evaluation."
    )


def evaluate_accuracy(
    question: str,
    response: str,
    reference_answer: str = "",
    source_context: str = "",
) -> AccuracyResult:
    """
    Evaluates factual correctness using a reference answer
    or retrieved source context.
    """

    reference_information = reference_answer.strip()

    if not reference_information:
        reference_information = source_context.strip()

    if not reference_information:
        reference_information = "No reference information was provided."

    prompt = f"""
You are a professional factual accuracy evaluator.

Evaluate whether the AI response is factually correct.

Use ONLY the supplied reference information as evidence.

Scoring criteria:

5 = Fully correct.
    All important factual claims are supported.

4 = Mostly correct.
    Main answer is correct with minor issues.

3 = Partially correct.
    Some important claims are correct and others are incomplete
    or incorrect.

2 = Mostly incorrect.
    Contains major factual errors but may contain some correct information.

1 = Completely incorrect.
    The central answer is factually wrong or contradicts the reference.

Important rules:

- Do not reward relevance.
- Do not assume unsupported information is true.
- Identify contradictions.
- Explain the score.
- Quote or summarize supporting evidence from the reference.

Question:
{question}

AI Response:
{response}

Reference Information:
{reference_information}

Return:
1. accuracy_score
2. reasoning
3. evidence
"""

    return generate_structured(prompt, AccuracyResult)