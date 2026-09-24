from typing import List, Literal

from pydantic import BaseModel, Field

from src.llm_client import generate_structured


# ============================================================
# Structured Output Model
# ============================================================

class CompletenessResult(BaseModel):
    completeness_score: Literal["1", "2", "3", "4", "5"] = Field(
        description="Completeness score from 1 to 5."
    )

    addressed_aspects: List[str] = Field(
        default_factory=list,
        description="Important aspects adequately addressed."
    )

    partial_aspects: List[str] = Field(
        default_factory=list,
        description="Important aspects partially addressed."
    )

    missing_aspects: List[str] = Field(
        default_factory=list,
        description="Important aspects missing from the response."
    )

    reasoning: str = Field(
        description="Reasoning explaining the completeness score."
    )


# ============================================================
# Completeness Judge
# ============================================================

def evaluate_completeness(
    question: str,
    response: str,
    reference_answer: str = "",
    source_context: str = ""
) -> CompletenessResult:

    reference_answer = reference_answer or ""
    source_context = source_context or ""

    reference_section = (
        f"""
REFERENCE ANSWER:
{reference_answer}
"""
        if reference_answer.strip()
        else
        """
REFERENCE ANSWER:
No reference answer was provided.
"""
    )

    source_section = (
        f"""
SOURCE CONTEXT:
{source_context}
"""
        if source_context.strip()
        else
        """
SOURCE CONTEXT:
No source context was provided.
"""
    )

    prompt = f"""
You are a Completeness Judge Agent in an AI Response Validation System.

Evaluate whether the AI-generated response sufficiently addresses
ALL important aspects of the question.

QUESTION:
{question}

AI RESPONSE:
{response}

{reference_section}

{source_section}

Instructions:

1. Identify the important requirements, sub-questions, or expected
   information contained in the question.

2. Compare the response against those requirements.

3. Categorize the important aspects into:
   - Adequately addressed
   - Partially addressed
   - Missing or insufficiently covered

4. If a reference answer is available, use it to identify information
   that should reasonably be covered.

5. If no reference answer is available but source context is provided,
   use the source context to determine relevant expected information.

6. Do not penalize the response for information that is not reasonably
   required by the question.

7. Do not require exact wording from the reference answer.

8. Use this scoring scale:

   5 = Fully complete.
       All important aspects are adequately addressed.

   4 = Mostly complete.
       Nearly all important aspects are addressed, with minor omissions.

   3 = Partially complete.
       Some important aspects are addressed, but meaningful information
       is missing or insufficiently explained.

   2 = Substantially incomplete.
       Several important aspects are missing.

   1 = Very incomplete.
       Most important requirements are not addressed.

IMPORTANT:
- Focus specifically on completeness.
- Do not judge writing style.
- Keep missing aspects specific.
- Do not mark an aspect missing if it was addressed.
- Provide concise but meaningful reasoning.

Return ONLY the structured evaluation result.
"""

    return generate_structured(
        prompt=prompt,
        response_schema=CompletenessResult
    )