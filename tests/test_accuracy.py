from src.agents.accuracy_judge import evaluate_accuracy


def test_correct_answer():

    result = evaluate_accuracy(
        question="Who created Python?",
        response="Python was created by Guido van Rossum.",
        reference_answer=(
            "Python was created by Guido van Rossum "
            "and first released in 1991."
        )
    )

    assert result.accuracy_score >= 4
    assert result.reasoning
    assert result.evidence


def test_incorrect_answer():

    result = evaluate_accuracy(
        question="Who created Python?",
        response="Python was created by James Gosling.",
        reference_answer=(
            "Python was created by Guido van Rossum."
        )
    )

    assert result.accuracy_score <= 2