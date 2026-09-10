import json

from src.evaluation.orchestrator import EvaluationOrchestrator


def main():

    question = "Who created Python?"

    response = (
        "Python was created by James Gosling in 1991."
    )

    reference_answer = (
        "Python was created by Guido van Rossum "
        "and first released in 1991."
    )

    source_context = """
    Python was created by Guido van Rossum.
    Python was first released in 1991.
    """

    orchestrator = EvaluationOrchestrator()

    result = orchestrator.evaluate(
        question=question,
        response=response,
        reference_answer=reference_answer,
        source_context=source_context
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


if __name__ == "__main__":
    main()