from src.evaluation.orchestrator import EvaluationOrchestrator


def test_complete_evaluation():

    orchestrator = EvaluationOrchestrator()

    result = orchestrator.evaluate(
        question="What is Python?",
        response=(
            "Python is a high-level programming language "
            "used for software development."
        ),
        reference_answer=(
            "Python is a high-level general-purpose "
            "programming language."
        ),
        source_context=(
            "Python is a high-level general-purpose "
            "programming language."
        )
    )

    assert "relevance" in result
    assert "accuracy" in result
    assert "hallucination" in result

    assert "relevance_score" in result["relevance"]
    assert "accuracy_score" in result["accuracy"]

    assert "hallucination_detected" in result["hallucination"]