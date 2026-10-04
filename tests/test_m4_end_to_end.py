"""M4 end-to-end tests for the AI Response Validation System.

These tests mock the Gemini/LLM layer so the E2E workflow can be verified
without consuming API quota. They validate data flow, scoring, verdict rules,
batch handling, dashboard statistics, and PDF report generation.
"""

from types import SimpleNamespace

import pandas as pd
import pytest


class _ModelNamespace(SimpleNamespace):
    def model_dump(self):
        return dict(vars(self))


def _dump_model(value):
    """Support both Pydantic models and lightweight test doubles."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict") and callable(value.dict):
        return value.dict()
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return value


# ---------------------------------------------------------------------------
# Single-evaluation E2E flow
# ---------------------------------------------------------------------------

def test_single_evaluation_end_to_end(monkeypatch):
    """Question/response -> judges -> verdict -> final result."""
    from src.evaluation import orchestrator as orchestrator_module

    relevance = _ModelNamespace(relevance_score="5", reasoning="Directly answers the question.")
    accuracy = _ModelNamespace(
        accuracy_score="5",
        reasoning="Matches the supplied reference.",
        evidence="Reference supports the answer.",
    )
    hallucination = _ModelNamespace(
        hallucination_detected=False,
        flagged_claims=[],
        overall_reasoning="No unsupported claims found.",
    )
    completeness = _ModelNamespace(
        completeness_score="5",
        addressed_aspects=["Main requirement"],
        partial_aspects=[],
        missing_aspects=[],
        reasoning="All required aspects are covered.",
    )

    monkeypatch.setattr(orchestrator_module, "evaluate_relevance", lambda **_: relevance)
    monkeypatch.setattr(orchestrator_module, "evaluate_accuracy", lambda **_: accuracy)
    monkeypatch.setattr(orchestrator_module, "detect_hallucinations", lambda **_: hallucination)
    monkeypatch.setattr(orchestrator_module, "evaluate_completeness", lambda **_: completeness)

    result = orchestrator_module.EvaluationOrchestrator().evaluate(
        question="What is Python?",
        response="Python is a high-level programming language.",
        reference_answer="Python is a high-level programming language.",
        source_context="Python is a programming language.",
    )

    assert result["question"] == "What is Python?"
    assert result["response"]
    assert result["relevance"]["relevance_score"] == "5"
    assert result["accuracy"]["accuracy_score"] == "5"
    assert result["completeness"]["completeness_score"] == "5"
    assert result["hallucination"]["hallucination_detected"] is False
    assert result["verdict"]["overall_score"] == 5.0
    assert result["verdict"]["verdict"] == "Pass"


# ---------------------------------------------------------------------------
# Verdict / critical-failure rules
# ---------------------------------------------------------------------------

def test_hallucination_forces_fail():
    from src.agents.verdict_agent import generate_verdict

    result = generate_verdict(
        relevance=_ModelNamespace(relevance_score="5"),
        accuracy=_ModelNamespace(accuracy_score="5"),
        completeness=_ModelNamespace(completeness_score="5", missing_aspects=[]),
        hallucination=_ModelNamespace(hallucination_detected=True),
    )

    assert result.verdict == "Fail"
    assert result.hallucination_score == 1


def test_accuracy_score_one_forces_fail():
    from src.agents.verdict_agent import generate_verdict

    result = generate_verdict(
        relevance=_ModelNamespace(relevance_score="5"),
        accuracy=_ModelNamespace(accuracy_score="1"),
        completeness=_ModelNamespace(completeness_score="5", missing_aspects=[]),
        hallucination=_ModelNamespace(hallucination_detected=False),
    )

    assert result.verdict == "Fail"


# ---------------------------------------------------------------------------
# Batch E2E flow
# ---------------------------------------------------------------------------

def _fake_batch_evaluation():
    return _ModelNamespace(
        evaluations=[
            _ModelNamespace(
                row_id=1,
                question="What is Python?",
                ai_response="Python is a programming language.",
                relevance_score="5",
                accuracy_score="5",
                completeness_score="5",
                hallucination_detected=False,
                flagged_claims=[],
                addressed_aspects=["Definition"],
                partial_aspects=[],
                missing_aspects=[],
                relevance_reasoning="Relevant.",
                accuracy_reasoning="Correct.",
                completeness_reasoning="Complete.",
                hallucination_reasoning="No hallucination.",
            ),
            _ModelNamespace(
                row_id=2,
                question="What is the capital of France?",
                ai_response="The capital is Berlin.",
                relevance_score="5",
                accuracy_score="1",
                completeness_score="5",
                hallucination_detected=True,
                flagged_claims=[
                    _ModelNamespace(
                        claim="The capital is Berlin.",
                        status="contradicted",
                        reasoning="Contradicts the reference/source.",
                        evidence="Paris is the capital of France.",
                    )
                ],
                addressed_aspects=["Capital requested"],
                partial_aspects=[],
                missing_aspects=[],
                relevance_reasoning="Relevant question.",
                accuracy_reasoning="Factually incorrect.",
                completeness_reasoning="The requested item was answered, but incorrectly.",
                hallucination_reasoning="Claim is contradicted by evidence.",
            ),
        ]
    )


def test_batch_evaluation_end_to_end(monkeypatch):
    from src.evaluation import batch_evaluator as batch_module

    monkeypatch.setattr(
        batch_module,
        "evaluate_entire_batch",
        lambda records: _fake_batch_evaluation(),
    )

    df = pd.DataFrame(
        [
            {
                "question": "What is Python?",
                "ai_response": "Python is a programming language.",
                "reference_answer": "Python is a programming language.",
                "source_context": "Python is a programming language.",
            },
            {
                "question": "What is the capital of France?",
                "ai_response": "The capital is Berlin.",
                "reference_answer": "The capital is Paris.",
                "source_context": "Paris is the capital of France.",
            },
        ]
    )

    result = batch_module.BatchEvaluator().evaluate_dataframe(df)

    assert result.total_rows == 2
    assert result.successful_rows == 2
    assert result.failed_rows == 0
    assert len(result.results) == 2
    assert result.results[0]["verdict"] == "Pass"
    assert result.results[1]["verdict"] == "Fail"
    assert result.statistics["pass_count"] == 1
    assert result.statistics["fail_count"] == 1
    assert result.statistics["hallucination_count"] == 1


# ---------------------------------------------------------------------------
# Input/error handling
# ---------------------------------------------------------------------------

def test_batch_rejects_missing_required_column():
    from src.evaluation.batch_evaluator import BatchEvaluator

    df = pd.DataFrame({"question": ["What is Python?"]})

    with pytest.raises(ValueError, match="Missing required column"):
        BatchEvaluator().evaluate_dataframe(df)


def test_batch_rejects_empty_dataframe():
    from src.evaluation.batch_evaluator import BatchEvaluator

    with pytest.raises(ValueError, match="empty"):
        BatchEvaluator().evaluate_dataframe(
            pd.DataFrame(columns=["question", "ai_response"])
        )


# ---------------------------------------------------------------------------
# Dashboard/statistics correctness
# ---------------------------------------------------------------------------

def test_dashboard_statistics_match_expected_values():
    from src.evaluation.batch_evaluator import BatchEvaluator

    results = [
        {
            "relevance_score": 5,
            "accuracy_score": 5,
            "completeness_score": 4,
            "hallucination_score": 5,
            "overall_score": 4.7,
            "verdict": "Pass",
            "hallucination_detected": False,
        },
        {
            "relevance_score": 4,
            "accuracy_score": 2,
            "completeness_score": 3,
            "hallucination_score": 1,
            "overall_score": 2.55,
            "verdict": "Fail",
            "hallucination_detected": True,
        },
    ]

    stats = BatchEvaluator().calculate_statistics(results)

    assert stats["average_relevance"] == 4.5
    assert stats["average_accuracy"] == 3.5
    assert stats["average_completeness"] == 3.5
    assert stats["average_hallucination"] == 3.0
    assert stats["average_overall_score"] == 3.62
    assert stats["pass_count"] == 1
    assert stats["needs_improvement_count"] == 0
    assert stats["fail_count"] == 1
    assert stats["hallucination_count"] == 1


# ---------------------------------------------------------------------------
# PDF export
# ---------------------------------------------------------------------------

def test_batch_pdf_export_end_to_end():
    from src.reporting.pdf_report import generate_batch_evaluation_pdf

    payload = {
        "total_rows": 2,
        "successful_rows": 2,
        "failed_rows": 0,
        "statistics": {
            "average_relevance": 4.5,
            "average_accuracy": 3.5,
            "average_completeness": 3.5,
            "average_hallucination": 3.0,
            "average_overall_score": 3.62,
            "pass_count": 1,
            "needs_improvement_count": 0,
            "fail_count": 1,
            "hallucination_count": 1,
        },
        "results": [
            {
                "row_id": 1,
                "question": "What is Python?",
                "ai_response": "Python is a programming language.",
                "relevance_score": 5,
                "accuracy_score": 5,
                "completeness_score": 4,
                "hallucination_score": 5,
                "hallucination_detected": False,
                "flagged_claims": [],
                "missing_aspects": [],
                "major_issues": [],
                "overall_score": 4.7,
                "verdict": "Pass",
                "verdict_reasoning": "Strong response.",
            },
            {
                "row_id": 2,
                "question": "What is the capital of France?",
                "ai_response": "The capital is Berlin.",
                "relevance_score": 5,
                "accuracy_score": 1,
                "completeness_score": 5,
                "hallucination_score": 1,
                "hallucination_detected": True,
                "flagged_claims": [
                    {
                        "claim": "The capital is Berlin.",
                        "status": "contradicted",
                        "reasoning": "Contradicted by source.",
                        "evidence": "Paris is the capital of France.",
                    }
                ],
                "missing_aspects": [],
                "major_issues": ["Unsupported or contradicted claims were detected."],
                "overall_score": 3.2,
                "verdict": "Fail",
                "verdict_reasoning": "Critical failure.",
            },
        ],
    }

    pdf = generate_batch_evaluation_pdf(payload)
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
