from types import SimpleNamespace

from src.agents.verdict_agent import generate_verdict


def create_mock_results(
    relevance="5",
    accuracy="5",
    completeness="5",
    hallucination=False
):

    relevance_result = SimpleNamespace(
        relevance_score=relevance
    )

    accuracy_result = SimpleNamespace(
        accuracy_score=accuracy
    )

    completeness_result = SimpleNamespace(
        completeness_score=completeness,
        missing_aspects=[]
    )

    hallucination_result = SimpleNamespace(
        hallucination_detected=hallucination
    )

    return (
        relevance_result,
        accuracy_result,
        hallucination_result,
        completeness_result
    )


def test_pass_verdict():

    (
        relevance,
        accuracy,
        hallucination,
        completeness
    ) = create_mock_results()

    result = generate_verdict(
        relevance,
        accuracy,
        hallucination,
        completeness
    )

    assert result.overall_score == 5.0
    assert result.verdict == "Pass"


def test_fail_when_hallucination_detected():

    (
        relevance,
        accuracy,
        hallucination,
        completeness
    ) = create_mock_results(
        hallucination=True
    )

    result = generate_verdict(
        relevance,
        accuracy,
        hallucination,
        completeness
    )

    assert result.verdict == "Fail"


def test_fail_when_accuracy_is_one():

    (
        relevance,
        accuracy,
        hallucination,
        completeness
    ) = create_mock_results(
        accuracy="1"
    )

    result = generate_verdict(
        relevance,
        accuracy,
        hallucination,
        completeness
    )

    assert result.verdict == "Fail"


def test_needs_improvement():

    (
        relevance,
        accuracy,
        hallucination,
        completeness
    ) = create_mock_results(
        relevance="3",
        accuracy="3",
        completeness="3"
    )

    result = generate_verdict(
        relevance,
        accuracy,
        hallucination,
        completeness
    )

    assert result.verdict == "Needs Improvement"