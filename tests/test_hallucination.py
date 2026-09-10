from src.agents.hallucination_detector import detect_hallucinations


def test_supported_response():

    context = """
    Python was created by Guido van Rossum.
    Python was first released in 1991.
    """

    response = (
        "Python was created by Guido van Rossum "
        "and first released in 1991."
    )

    result = detect_hallucinations(
        response=response,
        source_context=context
    )

    assert result.hallucination_detected is False
    assert len(result.flagged_claims) == 0


def test_hallucinated_claim():

    context = """
    Python was created by Guido van Rossum.
    Python was first released in 1991.
    """

    response = (
        "Python was created by James Gosling in 1991."
    )

    result = detect_hallucinations(
        response=response,
        source_context=context
    )

    assert result.hallucination_detected is True
    assert len(result.flagged_claims) > 0