from typing import List, Literal

from pydantic import BaseModel, Field

from src.llm_client import generate_structured


class FlaggedClaim(BaseModel):
    claim: str = Field(
        description="Specific unsupported or contradicted claim."
    )

    status: Literal[
        "unsupported",
        "contradicted"
    ] = Field(
        description="Whether the claim is unsupported or contradicted by the context."
    )

    reasoning: str = Field(
        description="Explanation of why the claim is problematic."
    )

    evidence: str = Field(
        description="Relevant evidence from the supplied context."
    )


class HallucinationResult(BaseModel):
    hallucination_detected: bool = Field(
        description="True if at least one unsupported or contradicted claim exists."
    )

    flagged_claims: List[FlaggedClaim] = Field(
        description="Specific claims that are unsupported or contradicted."
    )

    overall_reasoning: str = Field(
        description="Overall explanation of the hallucination evaluation."
    )


def detect_hallucinations(
    response: str,
    source_context: str
) -> HallucinationResult:

    prompt = f"""
You are a hallucination detection evaluator for an AI response validation system.

Your task is to determine whether the AI response contains factual claims
that are unsupported or contradicted by the supplied source context.

IMPORTANT:

1. Break the response into individual factual claims.
2. Check each claim against the source context.
3. A claim is SUPPORTED if the context clearly supports it.
4. A claim is CONTRADICTED if the context says something different.
5. A claim is UNSUPPORTED if the context does not provide evidence for it.
6. Do not flag opinions, greetings, or clearly non-factual language.
7. Flag SPECIFIC claims rather than declaring the whole response hallucinated.
8. Do not use outside knowledge.
9. If there are no unsupported or contradicted claims, return an empty list.

AI Response:
{response}

Source Context:
{source_context}

Return:
- hallucination_detected
- flagged_claims
- overall_reasoning
"""

    return generate_structured(prompt, HallucinationResult)