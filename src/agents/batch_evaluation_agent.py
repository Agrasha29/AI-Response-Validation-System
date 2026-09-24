from typing import List, Literal

from pydantic import BaseModel, Field

from src.llm_client import generate_structured


# ==========================================================
# FLAGGED HALLUCINATION CLAIM
# ==========================================================

class BatchFlaggedClaim(BaseModel):

    claim: str = Field(
        description="Specific unsupported or contradicted claim."
    )

    status: Literal[
        "unsupported",
        "contradicted"
    ] = Field(
        description="Whether the claim is unsupported or contradicted."
    )

    reasoning: str = Field(
        description="Why this claim is problematic."
    )

    evidence: str = Field(
        description="Relevant evidence from the reference information."
    )


# ==========================================================
# SINGLE ROW RESULT
# ==========================================================

class BatchRowEvaluation(BaseModel):

    row_number: int = Field(
        description="CSV row number."
    )

    relevance_score: Literal["1", "2", "3", "4", "5"]

    relevance_reasoning: str

    accuracy_score: Literal["1", "2", "3", "4", "5"]

    accuracy_reasoning: str

    accuracy_evidence: str

    hallucination_detected: bool

    flagged_claims: List[BatchFlaggedClaim] = Field(
        default_factory=list
    )

    hallucination_reasoning: str

    completeness_score: Literal["1", "2", "3", "4", "5"]

    completeness_reasoning: str

    addressed_aspects: List[str] = Field(
        default_factory=list
    )

    partial_aspects: List[str] = Field(
        default_factory=list
    )

    missing_aspects: List[str] = Field(
        default_factory=list
    )


# ==========================================================
# ENTIRE BATCH RESULT
# ==========================================================

class BatchEvaluationResponse(BaseModel):

    evaluations: List[BatchRowEvaluation]


# ==========================================================
# BATCH EVALUATOR
# ==========================================================

def evaluate_entire_batch(records: List[dict]) -> BatchEvaluationResponse:

    formatted_records = ""

    for record in records:

        formatted_records += f"""
--------------------------------------------------
CSV ROW: {record['row_number']}
--------------------------------------------------

QUESTION:
{record['question']}

AI RESPONSE:
{record['ai_response']}

REFERENCE ANSWER:
{record['reference_answer']}

SOURCE CONTEXT:
{record['source_context']}

"""

    prompt = f"""
You are the Batch Evaluation Agent in an AI Response
Validation System.

You will receive MULTIPLE CSV records.

Evaluate EVERY record across four dimensions:

1. Relevance
2. Accuracy
3. Hallucination
4. Completeness

IMPORTANT:

Perform all evaluations for ALL records in this ONE request.

Do not skip any CSV row.

==================================================
RELEVANCE
==================================================

5 = Completely relevant.
4 = Mostly relevant.
3 = Partially relevant.
2 = Mostly irrelevant.
1 = Completely irrelevant.

==================================================
ACCURACY
==================================================

Use ONLY the supplied reference answer or source context.

5 = Fully correct.
4 = Mostly correct.
3 = Partially correct.
2 = Mostly incorrect.
1 = Completely incorrect.

==================================================
HALLUCINATION
==================================================

Check individual factual claims.

SUPPORTED:
Clearly supported by the supplied information.

CONTRADICTED:
The supplied information says something different.

UNSUPPORTED:
The supplied information does not support the claim.

Do not flag opinions or greetings.

If there are no problematic claims:

hallucination_detected = false

and flagged_claims must be empty.

==================================================
COMPLETENESS
==================================================

Identify the important requirements or subquestions.

5 = Fully complete.
4 = Mostly complete.
3 = Partially complete.
2 = Substantially incomplete.
1 = Very incomplete.

Identify:

- addressed aspects
- partially addressed aspects
- missing aspects

==================================================
IMPORTANT RULES
==================================================

- Evaluate every CSV row.
- Preserve the original CSV row number.
- Do not skip records.
- Do not use outside knowledge.
- Use the supplied reference information.
- Keep evaluations independent.
- Return one evaluation object for every CSV row.

==================================================
CSV RECORDS
==================================================

{formatted_records}

Return ONLY the structured batch evaluation.
"""

    return generate_structured(
        prompt=prompt,
        response_schema=BatchEvaluationResponse
    )