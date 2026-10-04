from types import SimpleNamespace

from src.agents.verdict_agent import generate_verdict


def make_result(
    relevance,
    accuracy,
    completeness,
    hallucination=False,
    missing_aspects=None
):
    return SimpleNamespace(
        relevance_score=str(relevance),
        accuracy_score=str(accuracy),
        completeness_score=str(completeness),
        hallucination_detected=hallucination,
        missing_aspects=missing_aspects or []
    )


def test_high_quality_response():

    result = generate_verdict(
        relevance=make_result(5, 5, 5),
        accuracy=make_result(5, 5, 5),
        hallucination=make_result(
            5,
            5,
            5,
            hallucination=False
        ),
        completeness=make_result(5, 5, 5)
    )

    assert result.overall_score == 5.0
    assert result.verdict == "Pass"


def test_accuracy_critical_failure():

    result = generate_verdict(
        relevance=make_result(5, 5, 5),
        accuracy=make_result(1, 1, 1),
        hallucination=make_result(
            5,
            5,
            5,
            hallucination=False
        ),
        completeness=make_result(5, 5, 5)
    )

    assert result.verdict == "Fail"


def test_hallucination_causes_failure():

    result = generate_verdict(
        relevance=make_result(5, 5, 5),
        accuracy=make_result(5, 5, 5),
        hallucination=make_result(
            5,
            5,
            5,
            hallucination=True
        ),
        completeness=make_result(5, 5, 5)
    )

    assert result.verdict == "Fail"


def test_needs_improvement():

    result = generate_verdict(
        relevance=make_result(3, 3, 3),
        accuracy=make_result(3, 3, 3),
        hallucination=make_result(
            3,
            3,
            3,
            hallucination=False
        ),
        completeness=make_result(3, 3, 3)
    )

    assert result.verdict == "Needs Improvement"