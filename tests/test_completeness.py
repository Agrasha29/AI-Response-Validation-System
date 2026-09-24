from src.agents.completeness_judge import evaluate_completeness


def test_completeness_returns_valid_score():

    result = evaluate_completeness(
        question="What is Python?",
        response="Python is a high-level programming language."
    )

    assert result.completeness_score in {
        "1", "2", "3", "4", "5"
    }

    assert isinstance(
        result.addressed_aspects,
        list
    )

    assert isinstance(
        result.missing_aspects,
        list
    )

    assert isinstance(
        result.reasoning,
        str
    )