import pandas as pd
import streamlit as st

from src.evaluation.orchestrator import EvaluationOrchestrator
from src.evaluation.batch_evaluator import BatchEvaluator


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Response Validation System",
    page_icon="🤖",
    layout="wide"
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def make_display_safe(value):
    """
    Convert complex Python objects into strings so that
    Streamlit/PyArrow can safely display them in a dataframe.
    """

    if value is None:
        return ""

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, list):
        return "\n".join(
            make_display_safe(item)
            for item in value
        )

    if isinstance(value, tuple):
        return "\n".join(
            make_display_safe(item)
            for item in value
        )

    if isinstance(value, dict):
        return "\n".join(
            f"{key}: {make_display_safe(val)}"
            for key, val in value.items()
        )

    return str(value)


def make_dataframe_display_safe(df):
    """
    Convert all complex/object values in a dataframe into
    strings that Arrow can safely render.
    """

    display_df = df.copy()

    for column in display_df.columns:
        display_df[column] = display_df[column].apply(
            make_display_safe
        )

    return display_df


# ==========================================================
# HEADER
# ==========================================================

st.title("🤖 AI Response Validation System")

st.caption(
    "AI-generated response evaluation using Relevance, Accuracy, "
    "Hallucination Detection, Completeness and Weighted Verdict."
)


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("⚙️ Evaluation Mode")

mode = st.sidebar.radio(
    "Choose evaluation mode:",
    ["Single Evaluation", "Batch CSV Evaluation"]
)


# ==========================================================
# SINGLE EVALUATION
# ==========================================================

if mode == "Single Evaluation":

    st.header("📝 Single Response Evaluation")

    question = st.text_area(
        "Question",
        placeholder="Enter the user's question..."
    )

    response = st.text_area(
        "AI Response",
        placeholder="Enter the AI-generated response..."
    )

    reference_answer = st.text_area(
        "Reference Answer",
        placeholder="Optional reference answer..."
    )

    source_context = st.text_area(
        "Source Context",
        placeholder="Optional source/context information..."
    )

    if st.button("🔍 Evaluate Response", type="primary"):

        if not question.strip():

            st.error("Please enter a question.")

        elif not response.strip():

            st.error("Please enter an AI response.")

        else:

            with st.spinner("Evaluating response..."):

                try:

                    # ==================================================
                    # RUN ORCHESTRATOR
                    # ==================================================

                    orchestrator = EvaluationOrchestrator()

                    result = orchestrator.evaluate(
                        question=question,
                        response=response,
                        reference_answer=reference_answer,
                        source_context=source_context
                    )

                    st.success(
                        "Evaluation completed successfully!"
                    )

                    # ==================================================
                    # EXTRACT RESULTS
                    # ==================================================

                    relevance = result["relevance"]
                    accuracy = result["accuracy"]
                    hallucination = result["hallucination"]
                    completeness = result["completeness"]
                    verdict = result["verdict"]

                    # ==================================================
                    # SCORES
                    # ==================================================

                    st.subheader("📊 Evaluation Scores")

                    col1, col2, col3, col4, col5 = st.columns(5)

                    # --------------------------------------------------
                    # RELEVANCE
                    # --------------------------------------------------

                    with col1:

                        st.metric(
                            "Relevance",
                            f"{float(relevance['relevance_score']):.1f}/5"
                        )

                    # --------------------------------------------------
                    # ACCURACY
                    # --------------------------------------------------

                    with col2:

                        st.metric(
                            "Accuracy",
                            f"{float(accuracy['accuracy_score']):.1f}/5"
                        )

                    # --------------------------------------------------
                    # COMPLETENESS
                    # --------------------------------------------------

                    with col3:

                        st.metric(
                            "Completeness",
                            f"{float(completeness['completeness_score']):.1f}/5"
                        )

                    # --------------------------------------------------
                    # HALLUCINATION
                    # --------------------------------------------------

                    with col4:

                        hallucination_score = (
                            1
                            if hallucination["hallucination_detected"]
                            else 5
                        )

                        st.metric(
                            "Hallucination",
                            f"{hallucination_score:.1f}/5"
                        )

                    # --------------------------------------------------
                    # OVERALL
                    # --------------------------------------------------

                    with col5:

                        st.metric(
                            "Overall Score",
                            f"{float(verdict['overall_score']):.1f}/5"
                        )

                    # ==================================================
                    # FINAL VERDICT
                    # ==================================================

                    st.subheader("⚖️ Final Verdict")

                    final_verdict = verdict["verdict"]

                    if final_verdict == "Pass":

                        st.success(
                            f"✅ {final_verdict}"
                        )

                    elif final_verdict == "Needs Improvement":

                        st.warning(
                            f"⚠️ {final_verdict}"
                        )

                    else:

                        st.error(
                            f"❌ {final_verdict}"
                        )

                    # ==================================================
                    # MAJOR ISSUES
                    # ==================================================

                    st.subheader("🚨 Major Issues")

                    major_issues = verdict.get(
                        "major_issues",
                        []
                    )

                    if major_issues:

                        for issue in major_issues:

                            st.write(
                                f"• {make_display_safe(issue)}"
                            )

                    else:

                        st.write(
                            "No major issues detected."
                        )

                    # ==================================================
                    # CONSOLIDATED REASONING
                    # ==================================================

                    st.subheader("🧠 Consolidated Reasoning")

                    st.write(
                        make_display_safe(
                            verdict.get("reasoning", "")
                        )
                    )

                    # ==================================================
                    # RELEVANCE DETAILS
                    # ==================================================

                    with st.expander(
                        "🔎 Relevance Details"
                    ):

                        st.write(
                            f"**Score:** "
                            f"{relevance['relevance_score']}/5"
                        )

                        st.write(
                            "**Reasoning:**"
                        )

                        st.write(
                            make_display_safe(
                                relevance.get(
                                    "reasoning",
                                    ""
                                )
                            )
                        )

                    # ==================================================
                    # ACCURACY DETAILS
                    # ==================================================

                    with st.expander(
                        "🎯 Accuracy Details"
                    ):

                        st.write(
                            f"**Score:** "
                            f"{accuracy['accuracy_score']}/5"
                        )

                        st.write(
                            "**Reasoning:**"
                        )

                        st.write(
                            make_display_safe(
                                accuracy.get(
                                    "reasoning",
                                    ""
                                )
                            )
                        )

                        if accuracy.get("evidence"):

                            st.write(
                                "**Evidence:**"
                            )

                            st.write(
                                make_display_safe(
                                    accuracy["evidence"]
                                )
                            )

                    # ==================================================
                    # COMPLETENESS DETAILS
                    # ==================================================

                    with st.expander(
                        "🧩 Completeness Details"
                    ):

                        st.write(
                            f"**Score:** "
                            f"{completeness['completeness_score']}/5"
                        )

                        st.write(
                            "**Reasoning:**"
                        )

                        st.write(
                            make_display_safe(
                                completeness.get(
                                    "reasoning",
                                    ""
                                )
                            )
                        )

                        addressed_aspects = (
                            completeness.get(
                                "addressed_aspects",
                                []
                            )
                        )

                        partial_aspects = (
                            completeness.get(
                                "partial_aspects",
                                []
                            )
                        )

                        missing_aspects = (
                            completeness.get(
                                "missing_aspects",
                                []
                            )
                        )

                        if addressed_aspects:

                            st.write(
                                "**Addressed Aspects:**"
                            )

                            for aspect in addressed_aspects:

                                st.write(
                                    f"✅ {make_display_safe(aspect)}"
                                )

                        if partial_aspects:

                            st.write(
                                "**Partially Addressed:**"
                            )

                            for aspect in partial_aspects:

                                st.write(
                                    f"🟡 {make_display_safe(aspect)}"
                                )

                        if missing_aspects:

                            st.write(
                                "**Missing Aspects:**"
                            )

                            for aspect in missing_aspects:

                                st.write(
                                    f"❌ {make_display_safe(aspect)}"
                                )

                    # ==================================================
                    # HALLUCINATION DETAILS
                    # ==================================================

                    with st.expander(
                        "🚨 Hallucination Details"
                    ):

                        detected = hallucination.get(
                            "hallucination_detected",
                            False
                        )

                        if detected:

                            st.error(
                                "❌ Hallucination detected"
                            )

                            flagged_claims = (
                                hallucination.get(
                                    "flagged_claims",
                                    []
                                )
                            )

                            if flagged_claims:

                                st.write(
                                    "**Flagged Claims:**"
                                )

                                for claim in flagged_claims:

                                    if isinstance(
                                        claim,
                                        dict
                                    ):

                                        st.markdown(
                                            f"**Claim:** "
                                            f"{make_display_safe(claim.get('claim', ''))}"
                                        )

                                        st.write(
                                            f"**Status:** "
                                            f"{make_display_safe(claim.get('status', ''))}"
                                        )

                                        st.write(
                                            f"**Reasoning:** "
                                            f"{make_display_safe(claim.get('reasoning', ''))}"
                                        )

                                        if claim.get(
                                            "evidence"
                                        ):

                                            st.write(
                                                f"**Evidence:** "
                                                f"{make_display_safe(claim['evidence'])}"
                                            )

                                    else:

                                        st.write(
                                            make_display_safe(
                                                claim
                                            )
                                        )

                        else:

                            st.success(
                                "✅ No hallucination detected"
                            )

                        st.write(
                            "**Reasoning:**"
                        )

                        st.write(
                            make_display_safe(
                                hallucination.get(
                                    "overall_reasoning",
                                    ""
                                )
                            )
                        )

                except Exception as error:

                    st.error(
                        f"Evaluation failed: {error}"
                    )


# ==========================================================
# BATCH CSV EVALUATION
# ==========================================================

else:

    st.header("📂 Batch CSV Evaluation")

    st.write(
        "Upload a CSV file containing multiple question-response pairs."
    )

    st.info(
        """
Required columns:
- question
- ai_response

Optional columns:
- reference_answer
- source_context
"""
    )

    uploaded_file = st.file_uploader(
        "📤 Upload CSV",
        type=["csv"]
    )

    if uploaded_file:

        try:

            # ==================================================
            # READ CSV
            # ==================================================

            df = pd.read_csv(uploaded_file)

            st.subheader("📄 Uploaded Data")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # ==================================================
            # CREATE BATCH EVALUATOR
            # ==================================================

            batch_evaluator = BatchEvaluator()

            # ==================================================
            # VALIDATE CSV
            # ==================================================

            try:

                batch_evaluator.validate_dataframe(df)

                st.success(
                    f"CSV structure is valid — "
                    f"{len(df)} record(s) found."
                )

            except ValueError as validation_error:

                st.error(
                    str(validation_error)
                )

                st.stop()

            # ==================================================
            # BATCH INFORMATION
            # ==================================================

            st.info(
                f"Processing {len(df)} record(s) using "
                "one Gemini request for the complete batch."
            )

            # ==================================================
            # RUN BATCH
            # ==================================================

            if st.button(
                "🚀 Run Batch Evaluation",
                type="primary"
            ):

                progress = st.progress(0)

                status = st.empty()

                status.info(
                    f"Evaluating {len(df)} record(s)..."
                )

                try:

                    batch_result = (
                        batch_evaluator.evaluate_dataframe(
                            df
                        )
                    )

                    progress.progress(100)

                    status.success(
                        "Batch evaluation completed successfully."
                    )

                except Exception as error:

                    progress.progress(100)

                    status.error(
                        "Batch evaluation failed."
                    )

                    st.error(
                        f"Batch evaluation failed: {error}"
                    )

                    st.stop()

                # ==================================================
                # SUMMARY
                # ==================================================

                st.subheader("📊 Batch Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Total Rows",
                        batch_result.total_rows
                    )

                with col2:

                    st.metric(
                        "Successful",
                        batch_result.successful_rows
                    )

                with col3:

                    st.metric(
                        "Failed",
                        batch_result.failed_rows
                    )

                with col4:

                    average_score = (
                        batch_result.statistics.get(
                            "average_overall_score",
                            0
                        )
                    )

                    st.metric(
                        "Average Overall Score",
                        f"{average_score:.2f}/5"
                    )

                # ==================================================
                # RESULTS TABLE
                # ==================================================

                st.subheader("📋 Evaluation Results")

                if batch_result.results:

                    results_df = pd.DataFrame(
                        batch_result.results
                    )

                    display_results_df = (
                        make_dataframe_display_safe(
                            results_df
                        )
                    )

                    st.dataframe(
                        display_results_df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.warning(
                        "No evaluation results were generated."
                    )

                # ==================================================
                # STATISTICS
                # ==================================================

                stats = batch_result.statistics

                st.subheader("📈 Aggregate Statistics")

                stat_col1, stat_col2, stat_col3, stat_col4 = (
                    st.columns(4)
                )

                with stat_col1:

                    st.metric(
                        "Avg Relevance",
                        f"{stats.get('average_relevance', 0):.2f}/5"
                    )

                with stat_col2:

                    st.metric(
                        "Avg Accuracy",
                        f"{stats.get('average_accuracy', 0):.2f}/5"
                    )

                with stat_col3:

                    st.metric(
                        "Avg Completeness",
                        f"{stats.get('average_completeness', 0):.2f}/5"
                    )

                with stat_col4:

                    st.metric(
                        "Avg Hallucination",
                        f"{stats.get('average_hallucination', 0):.2f}/5"
                    )

                # ==================================================
                # VERDICT DISTRIBUTION
                # ==================================================

                st.subheader("⚖️ Verdict Distribution")

                if batch_result.results:

                    verdict_series = pd.Series(
                        [
                            item.get("verdict")
                            for item in batch_result.results
                            if item.get("verdict")
                        ]
                    )

                    if not verdict_series.empty:

                        verdict_counts = (
                            verdict_series
                            .value_counts()
                            .rename_axis("Verdict")
                            .reset_index(name="Count")
                        )

                        st.bar_chart(
                            verdict_counts,
                            x="Verdict",
                            y="Count"
                        )

                # ==================================================
                # DIMENSION SCORES
                # ==================================================

                st.subheader(
                    "📊 Average Dimension Scores"
                )

                dimension_data = pd.DataFrame(
                    {
                        "Dimension": [
                            "Relevance",
                            "Accuracy",
                            "Completeness",
                            "Hallucination"
                        ],
                        "Average Score": [
                            stats.get(
                                "average_relevance",
                                0
                            ),
                            stats.get(
                                "average_accuracy",
                                0
                            ),
                            stats.get(
                                "average_completeness",
                                0
                            ),
                            stats.get(
                                "average_hallucination",
                                0
                            )
                        ]
                    }
                )

                st.bar_chart(
                    dimension_data,
                    x="Dimension",
                    y="Average Score"
                )

                # ==================================================
                # FAILED EVALUATIONS
                # ==================================================

                failed_results = [
                    item
                    for item in batch_result.results
                    if item.get("verdict")
                    == "Evaluation Error"
                ]

                if failed_results:

                    st.subheader(
                        "❌ Failed Evaluations"
                    )

                    failed_df = pd.DataFrame(
                        failed_results
                    )

                    failed_display_df = (
                        make_dataframe_display_safe(
                            failed_df
                        )
                    )

                    st.dataframe(
                        failed_display_df,
                        use_container_width=True,
                        hide_index=True
                    )

        except Exception as error:

            st.error(
                f"Could not read CSV file: {error}"
            )