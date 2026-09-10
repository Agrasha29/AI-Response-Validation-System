from src.agents.relevance_judge import evaluate_relevance


def test_fully_relevant():

    result = evaluate_relevance(
        question="What is Python?",
        response=(
            "Python is a high-level programming language "
            "used for software development and data science."
        )
    )

    assert 1 <= result.relevance_score <= 5
    assert result.reasoning


def test_irrelevant_response():

    result = evaluate_relevance(
        question="What is Python?",
        response="Pizza is one of the most popular foods."
    )

    assert result.relevance_score <= 2