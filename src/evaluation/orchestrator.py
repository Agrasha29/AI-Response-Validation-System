from typing import Dict, Optional

from src.agents.relevance_judge import evaluate_relevance
from src.agents.accuracy_judge import evaluate_accuracy
from src.agents.hallucination_detector import detect_hallucinations


class EvaluationOrchestrator:

    def evaluate(
        self,
        question: str,
        response: str,
        reference_answer: Optional[str] = None,
        source_context: Optional[str] = None
    ) -> Dict:

        reference_answer = reference_answer or ""
        source_context = source_context or ""

        # ---------------------------
        # 1. Relevance Evaluation
        # ---------------------------

        relevance_result = evaluate_relevance(
            question=question,
            response=response
        )

        # ---------------------------
        # 2. Accuracy Evaluation
        # ---------------------------

        accuracy_result = evaluate_accuracy(
            question=question,
            response=response,
            reference_answer=reference_answer,
            source_context=source_context
        )

        # ---------------------------
        # 3. Hallucination Detection
        # ---------------------------

        hallucination_result = detect_hallucinations(
            response=response,
            source_context=source_context
        )

        # ---------------------------
        # Final Evaluation
        # ---------------------------

        return {
            "question": question,
            "response": response,

            "relevance": relevance_result.model_dump(),

            "accuracy": accuracy_result.model_dump(),

            "hallucination": hallucination_result.model_dump()
        }
    