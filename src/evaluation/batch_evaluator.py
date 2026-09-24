import pandas as pd

from src.agents.batch_evaluation_agent import evaluate_entire_batch
from src.agents.verdict_agent import generate_verdict


class BatchEvaluationResult:

    def __init__(self):
        self.results = []
        self.total_rows = 0
        self.successful_rows = 0
        self.failed_rows = 0
        self.statistics = {}


class BatchEvaluator:

    REQUIRED_COLUMNS = [
        "question",
        "ai_response"
    ]

    OPTIONAL_COLUMNS = [
        "reference_answer",
        "source_context"
    ]

    # ==========================================================
    # VALIDATE DATAFRAME
    # ==========================================================

    def validate_dataframe(self, df: pd.DataFrame):

        if not isinstance(df, pd.DataFrame):
            raise ValueError(
                "Invalid input. Expected a pandas DataFrame."
            )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required column(s): "
                + ", ".join(missing_columns)
            )

        if df.empty:
            raise ValueError(
                "The uploaded CSV file is empty."
            )

        return True

    # ==========================================================
    # PREPARE RECORDS
    # ==========================================================

    def prepare_records(self, df: pd.DataFrame):

        records = []

        for index, row in df.iterrows():

            question = str(
                row.get("question", "")
            ).strip()

            ai_response = str(
                row.get("ai_response", "")
            ).strip()

            reference_answer = str(
                row.get("reference_answer", "")
            ).strip()

            source_context = str(
                row.get("source_context", "")
            ).strip()

            # --------------------------------------------------
            # Skip invalid rows
            # --------------------------------------------------

            if not question or not ai_response:
                continue

            row_id = index + 1

            # --------------------------------------------------
            # IMPORTANT
            #
            # Some parts of the batch agent use row_number,
            # while the rest of the application uses row_id.
            #
            # We provide BOTH fields so the entire pipeline
            # remains compatible.
            # --------------------------------------------------

            records.append(
                {
                    "row_id": row_id,
                    "row_number": row_id,
                    "question": question,
                    "ai_response": ai_response,
                    "reference_answer": reference_answer,
                    "source_context": source_context
                }
            )

        return records

    # ==========================================================
    # MAIN BATCH EVALUATION
    # ==========================================================

    def evaluate_dataframe(self, df: pd.DataFrame):

        # ------------------------------------------------------
        # Validate CSV
        # ------------------------------------------------------

        self.validate_dataframe(df)

        batch_result = BatchEvaluationResult()

        batch_result.total_rows = len(df)

        # ------------------------------------------------------
        # Prepare valid records
        # ------------------------------------------------------

        records = self.prepare_records(df)

        if not records:

            raise ValueError(
                "No valid records were found in the CSV. "
                "Each row must contain both question and ai_response."
            )

        # ------------------------------------------------------
        # ONE GEMINI REQUEST FOR THE ENTIRE BATCH
        # ------------------------------------------------------

        try:

            batch_response = evaluate_entire_batch(
                records=records
            )

        except Exception as e:

            raise RuntimeError(
                f"Batch evaluation failed: {str(e)}"
            ) from e

        # ------------------------------------------------------
        # CHECK BATCH RESPONSE
        # ------------------------------------------------------

        if batch_response is None:

            raise RuntimeError(
                "Batch evaluation returned no response."
            )

        if not hasattr(batch_response, "evaluations"):

            raise RuntimeError(
                "Batch evaluation response does not contain "
                "'evaluations'."
            )

        if batch_response.evaluations is None:

            raise RuntimeError(
                "Batch evaluation returned an empty evaluations list."
            )

        # ------------------------------------------------------
        # PROCESS EACH EVALUATION
        # ------------------------------------------------------

        for evaluation in batch_response.evaluations:

            try:

                # ==================================================
                # GET ROW ID SAFELY
                # ==================================================

                row_id = getattr(
                    evaluation,
                    "row_id",
                    None
                )

                if row_id is None:

                    row_id = getattr(
                        evaluation,
                        "row_number",
                        None
                    )

                # ==================================================
                # GET BASIC DATA
                # ==================================================

                question = getattr(
                    evaluation,
                    "question",
                    ""
                )

                ai_response = getattr(
                    evaluation,
                    "ai_response",
                    ""
                )

                # ==================================================
                # CREATE LOCAL SCORE OBJECTS
                # ==================================================

                class ScoreObject:
                    pass

                # --------------------------------------------------
                # RELEVANCE
                # --------------------------------------------------

                relevance = ScoreObject()

                relevance.relevance_score = getattr(
                    evaluation,
                    "relevance_score",
                    0
                )

                # --------------------------------------------------
                # ACCURACY
                # --------------------------------------------------

                accuracy = ScoreObject()

                accuracy.accuracy_score = getattr(
                    evaluation,
                    "accuracy_score",
                    0
                )

                # --------------------------------------------------
                # COMPLETENESS
                # --------------------------------------------------

                completeness = ScoreObject()

                completeness.completeness_score = getattr(
                    evaluation,
                    "completeness_score",
                    0
                )

                completeness.missing_aspects = getattr(
                    evaluation,
                    "missing_aspects",
                    []
                )

                # --------------------------------------------------
                # HALLUCINATION
                # --------------------------------------------------

                hallucination = ScoreObject()

                hallucination.hallucination_detected = getattr(
                    evaluation,
                    "hallucination_detected",
                    False
                )

                # ==================================================
                # GENERATE FINAL VERDICT
                # ==================================================

                verdict = generate_verdict(
                    relevance=relevance,
                    accuracy=accuracy,
                    hallucination=hallucination,
                    completeness=completeness
                )

                # ==================================================
                # STORE FINAL RESULT
                # ==================================================

                batch_result.results.append(
                    {
                        "row_id": row_id,

                        "question": question,

                        "ai_response": ai_response,

                        # ------------------------------
                        # Dimension Scores
                        # ------------------------------

                        "relevance_score": int(
                            getattr(
                                evaluation,
                                "relevance_score",
                                0
                            )
                        ),

                        "accuracy_score": int(
                            getattr(
                                evaluation,
                                "accuracy_score",
                                0
                            )
                        ),

                        "completeness_score": int(
                            getattr(
                                evaluation,
                                "completeness_score",
                                0
                            )
                        ),

                        # Hallucination:
                        # 1 = detected
                        # 5 = not detected
                        "hallucination_score": (
                            1
                            if getattr(
                                evaluation,
                                "hallucination_detected",
                                False
                            )
                            else 5
                        ),

                        # ------------------------------
                        # Hallucination Details
                        # ------------------------------

                        "hallucination_detected": getattr(
                            evaluation,
                            "hallucination_detected",
                            False
                        ),

                        "flagged_claims": getattr(
                            evaluation,
                            "flagged_claims",
                            []
                        ),

                        # ------------------------------
                        # Completeness Details
                        # ------------------------------

                        "addressed_aspects": getattr(
                            evaluation,
                            "addressed_aspects",
                            []
                        ),

                        "partial_aspects": getattr(
                            evaluation,
                            "partial_aspects",
                            []
                        ),

                        "missing_aspects": getattr(
                            evaluation,
                            "missing_aspects",
                            []
                        ),

                        # ------------------------------
                        # Agent Reasoning
                        # ------------------------------

                        "relevance_reasoning": getattr(
                            evaluation,
                            "relevance_reasoning",
                            ""
                        ),

                        "accuracy_reasoning": getattr(
                            evaluation,
                            "accuracy_reasoning",
                            ""
                        ),

                        "completeness_reasoning": getattr(
                            evaluation,
                            "completeness_reasoning",
                            ""
                        ),

                        "hallucination_reasoning": getattr(
                            evaluation,
                            "hallucination_reasoning",
                            ""
                        ),

                        # ------------------------------
                        # FINAL VERDICT
                        # ------------------------------

                        "overall_score": verdict.overall_score,

                        "verdict": verdict.verdict,

                        "major_issues": verdict.major_issues,

                        "verdict_reasoning": verdict.reasoning
                    }
                )

                batch_result.successful_rows += 1

            except Exception as e:

                # --------------------------------------------------
                # Get row information safely
                # --------------------------------------------------

                row_id = getattr(
                    evaluation,
                    "row_id",
                    None
                )

                if row_id is None:

                    row_id = getattr(
                        evaluation,
                        "row_number",
                        None
                    )

                question = getattr(
                    evaluation,
                    "question",
                    ""
                )

                ai_response = getattr(
                    evaluation,
                    "ai_response",
                    ""
                )

                # --------------------------------------------------
                # Continue processing remaining rows
                # --------------------------------------------------

                batch_result.failed_rows += 1

                batch_result.results.append(
                    {
                        "row_id": row_id,

                        "question": question,

                        "ai_response": ai_response,

                        "relevance_score": None,

                        "accuracy_score": None,

                        "completeness_score": None,

                        "hallucination_score": None,

                        "hallucination_detected": None,

                        "flagged_claims": [],

                        "addressed_aspects": [],

                        "partial_aspects": [],

                        "missing_aspects": [],

                        "relevance_reasoning": "",

                        "accuracy_reasoning": "",

                        "completeness_reasoning": "",

                        "hallucination_reasoning": "",

                        "overall_score": None,

                        "verdict": "Evaluation Error",

                        "major_issues": [
                            str(e)
                        ],

                        "verdict_reasoning": (
                            "Unable to generate final verdict: "
                            + str(e)
                        )
                    }
                )

        # ------------------------------------------------------
        # CALCULATE STATISTICS
        # ------------------------------------------------------

        batch_result.statistics = (
            self.calculate_statistics(
                batch_result.results
            )
        )

        return batch_result

    # ==========================================================
    # CALCULATE STATISTICS
    # ==========================================================

    def calculate_statistics(self, results):

        empty_statistics = {
            "average_relevance": 0,
            "average_accuracy": 0,
            "average_completeness": 0,
            "average_hallucination": 0,
            "average_overall_score": 0,
            "pass_count": 0,
            "needs_improvement_count": 0,
            "fail_count": 0,
            "hallucination_count": 0
        }

        if not results:
            return empty_statistics

        results_df = pd.DataFrame(results)

        # ------------------------------------------------------
        # Only successful numerical evaluations
        # ------------------------------------------------------

        if "overall_score" not in results_df.columns:
            return empty_statistics

        valid_df = results_df[
            results_df["overall_score"].notna()
        ]

        if valid_df.empty:
            return empty_statistics

        # ------------------------------------------------------
        # AVERAGES
        # ------------------------------------------------------

        average_relevance = round(
            pd.to_numeric(
                valid_df["relevance_score"],
                errors="coerce"
            ).mean(),
            2
        )

        average_accuracy = round(
            pd.to_numeric(
                valid_df["accuracy_score"],
                errors="coerce"
            ).mean(),
            2
        )

        average_completeness = round(
            pd.to_numeric(
                valid_df["completeness_score"],
                errors="coerce"
            ).mean(),
            2
        )

        average_hallucination = round(
            pd.to_numeric(
                valid_df["hallucination_score"],
                errors="coerce"
            ).mean(),
            2
        )

        average_overall_score = round(
            pd.to_numeric(
                valid_df["overall_score"],
                errors="coerce"
            ).mean(),
            2
        )

        # ------------------------------------------------------
        # VERDICT COUNTS
        # ------------------------------------------------------

        pass_count = (
            valid_df["verdict"] == "Pass"
        ).sum()

        needs_improvement_count = (
            valid_df["verdict"] == "Needs Improvement"
        ).sum()

        fail_count = (
            valid_df["verdict"] == "Fail"
        ).sum()

        # ------------------------------------------------------
        # HALLUCINATION COUNT
        # ------------------------------------------------------

        hallucination_count = (
            valid_df["hallucination_detected"] == True
        ).sum()

        # ------------------------------------------------------
        # RETURN STATISTICS
        # ------------------------------------------------------

        return {
            "average_relevance": (
                0
                if pd.isna(average_relevance)
                else average_relevance
            ),

            "average_accuracy": (
                0
                if pd.isna(average_accuracy)
                else average_accuracy
            ),

            "average_completeness": (
                0
                if pd.isna(average_completeness)
                else average_completeness
            ),

            "average_hallucination": (
                0
                if pd.isna(average_hallucination)
                else average_hallucination
            ),

            "average_overall_score": (
                0
                if pd.isna(average_overall_score)
                else average_overall_score
            ),

            "pass_count": int(
                pass_count
            ),

            "needs_improvement_count": int(
                needs_improvement_count
            ),

            "fail_count": int(
                fail_count
            ),

            "hallucination_count": int(
                hallucination_count
            )
        }