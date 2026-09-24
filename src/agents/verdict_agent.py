from typing import Literal
from pydantic import BaseModel, Field


# ---------------------------------
# Verdict Result Schema
# ---------------------------------

class VerdictResult(BaseModel):
    relevance_score: float = Field(...)
    accuracy_score: float = Field(...)
    completeness_score: float = Field(...)
    hallucination_score: float = Field(...)

    overall_score: float = Field(...)

    verdict: Literal[
        "Pass",
        "Needs Improvement",
        "Fail"
    ] = Field(...)

    major_issues: list[str] = Field(default_factory=list)

    reasoning: str = Field(...)


# ---------------------------------
# Weighted Scoring Configuration
# ---------------------------------

RELEVANCE_WEIGHT = 0.25
ACCURACY_WEIGHT = 0.30
COMPLETENESS_WEIGHT = 0.25
HALLUCINATION_WEIGHT = 0.20


# ---------------------------------
# Verdict Generation
# ---------------------------------

def generate_verdict(
    relevance,
    accuracy,
    hallucination,
    completeness
) -> VerdictResult:

    # Convert scores from strings to numbers
    relevance_score = int(relevance.relevance_score)
    accuracy_score = int(accuracy.accuracy_score)
    completeness_score = int(completeness.completeness_score)

    # Hallucination is currently boolean
    # No hallucination = 5
    # Hallucination detected = 1
    hallucination_score = (
        1 if hallucination.hallucination_detected else 5
    )

    # ---------------------------------
    # Weighted Overall Score
    # ---------------------------------

    overall_score = (
        relevance_score * RELEVANCE_WEIGHT
        + accuracy_score * ACCURACY_WEIGHT
        + completeness_score * COMPLETENESS_WEIGHT
        + hallucination_score * HALLUCINATION_WEIGHT
    )

    overall_score = round(overall_score, 2)

    # ---------------------------------
    # Identify Major Issues
    # ---------------------------------

    major_issues = []

    if relevance_score <= 2:
        major_issues.append(
            "The response is not sufficiently relevant to the question."
        )

    if accuracy_score <= 2:
        major_issues.append(
            "The response contains significant factual inaccuracies."
        )

    if completeness_score <= 2:
        major_issues.append(
            "The response is substantially incomplete."
        )

    if hallucination.hallucination_detected:
        major_issues.append(
            "Unsupported or contradicted claims were detected."
        )

    # ---------------------------------
    # Final Verdict
    # ---------------------------------

    # Critical failure condition
    if accuracy_score == 1 or hallucination.hallucination_detected:
        verdict = "Fail"

    elif overall_score >= 4.0:
        verdict = "Pass"

    elif overall_score >= 2.5:
        verdict = "Needs Improvement"

    else:
        verdict = "Fail"

    # ---------------------------------
    # Consolidated Reasoning
    # ---------------------------------

    reasoning = (
        f"The response received a relevance score of "
        f"{relevance_score}/5, an accuracy score of "
        f"{accuracy_score}/5, a completeness score of "
        f"{completeness_score}/5, and a hallucination score of "
        f"{hallucination_score}/5. "
        f"Using the defined weighted scoring model, the overall "
        f"score is {overall_score}/5. "
        f"The final verdict is '{verdict}'."
    )

    return VerdictResult(
        relevance_score=relevance_score,
        accuracy_score=accuracy_score,
        completeness_score=completeness_score,
        hallucination_score=hallucination_score,
        overall_score=overall_score,
        verdict=verdict,
        major_issues=major_issues,
        reasoning=reasoning
    )