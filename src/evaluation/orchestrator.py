from typing import Dict, Optional

from src.agents.relevance_judge import evaluate_relevance
from src.agents.accuracy_judge import evaluate_accuracy
from src.agents.hallucination_detector import detect_hallucinations
from src.agents.completeness_judge import evaluate_completeness
from src.agents.verdict_agent import generate_verdict


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
        # 4. Completeness Evaluation
        # ---------------------------

        completeness_result = evaluate_completeness(
            question=question,
            response=response,
            reference_answer=reference_answer,
            source_context=source_context
        )

        # ---------------------------
        # 5. Overall Verdict
        # ---------------------------

        verdict_result = generate_verdict(
            relevance=relevance_result,
            accuracy=accuracy_result,
            hallucination=hallucination_result,
            completeness=completeness_result
        )

        # ---------------------------
        # Final Evaluation Result
        # ---------------------------

        return {
            "question": question,
            "response": response,

            "relevance": relevance_result.model_dump(),

            "accuracy": accuracy_result.model_dump(),

            "hallucination": hallucination_result.model_dump(),

            "completeness": completeness_result.model_dump(),

            "verdict": verdict_result.model_dump()
        }