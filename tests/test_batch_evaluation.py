import pandas as pd

from src.evaluation.batch_evaluator import BatchEvaluator


def test_valid_csv_columns():

    evaluator = BatchEvaluator()

    df = pd.DataFrame({
        "question": [
            "What is Python?"
        ],
        "ai_response": [
            "Python is a programming language."
        ]
    })

    errors = evaluator.validate_dataframe(df)

    assert errors == []


def test_missing_required_column():

    evaluator = BatchEvaluator()

    df = pd.DataFrame({
        "question": [
            "What is Python?"
        ]
    })

    errors = evaluator.validate_dataframe(df)

    assert len(errors) == 1
    assert "ai_response" in errors[0]


def test_batch_statistics():

    results = [
        {
            "relevance_score": "5",
            "accuracy_score": "5",
            "completeness_score": "4",
            "overall_score": 4.7,
            "verdict": "Pass",
            "hallucination_detected": False
        },
        {
            "relevance_score": "3",
            "accuracy_score": "3",
            "completeness_score": "2",
            "overall_score": 2.7,
            "verdict": "Needs Improvement",
            "hallucination_detected": False
        },
        {
            "relevance_score": "2",
            "accuracy_score": "1",
            "completeness_score": "2",
            "overall_score": 1.8,
            "verdict": "Fail",
            "hallucination_detected": True
        }
    ]

    statistics = BatchEvaluator.calculate_statistics(
        results
    )

    assert statistics["total_evaluated"] == 3
    assert statistics["pass_count"] == 1
    assert statistics["needs_improvement_count"] == 1
    assert statistics["fail_count"] == 1
    assert statistics["hallucination_count"] == 1