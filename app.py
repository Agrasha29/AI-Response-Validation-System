import streamlit as st

from src.evaluation.orchestrator import EvaluationOrchestrator


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Response Validation System",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🤖 AI Response Validation System")

st.markdown(
    """
    Evaluate AI-generated responses for:

    **Relevance • Accuracy • Hallucination**
    """
)

st.divider()


# --------------------------------------------------
# Input Section
# --------------------------------------------------

st.subheader("📝 Evaluation Input")

question = st.text_area(
    "Question",
    placeholder="Enter the user's question...",
    height=100
)

response = st.text_area(
    "AI Response",
    placeholder="Enter the AI-generated response...",
    height=150
)

reference_answer = st.text_area(
    "Reference Answer (Optional)",
    placeholder="Enter the expected/reference answer...",
    height=120
)

source_context = st.text_area(
    "Source Context (Optional)",
    placeholder="Enter retrieved source content...",
    height=150
)


# --------------------------------------------------
# Evaluation Button
# --------------------------------------------------

if st.button(
    "🔍 Evaluate Response",
    type="primary",
    use_container_width=True
):

    if not question.strip():
        st.warning("Please enter a question.")

    elif not response.strip():
        st.warning("Please enter an AI response.")

    else:

        with st.spinner("Evaluating AI response..."):

            try:

                orchestrator = EvaluationOrchestrator()

                result = orchestrator.evaluate(
                    question=question,
                    response=response,
                    reference_answer=reference_answer,
                    source_context=source_context
                )

                st.success("Evaluation completed successfully!")

                st.divider()

                # --------------------------------------------------
                # Results
                # --------------------------------------------------

                st.subheader("📊 Evaluation Results")

                relevance = result["relevance"]
                accuracy = result["accuracy"]
                hallucination = result["hallucination"]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "🎯 Relevance",
                        f"{relevance['relevance_score']}/5"
                    )

                with col2:
                    st.metric(
                        "✅ Accuracy",
                        f"{accuracy['accuracy_score']}/5"
                    )

                with col3:

                    if hallucination["hallucination_detected"]:
                        st.metric(
                            "🚨 Hallucination",
                            "Detected"
                        )
                    else:
                        st.metric(
                            "🟢 Hallucination",
                            "Not Detected"
                        )

                # --------------------------------------------------
                # Relevance
                # --------------------------------------------------

                st.subheader("🎯 Relevance Evaluation")

                st.write(
                    f"**Score:** {relevance['relevance_score']}/5"
                )

                st.info(
                    relevance["reasoning"]
                )

                # --------------------------------------------------
                # Accuracy
                # --------------------------------------------------

                st.subheader("✅ Accuracy Evaluation")

                st.write(
                    f"**Score:** {accuracy['accuracy_score']}/5"
                )

                st.info(
                    accuracy["reasoning"]
                )

                if accuracy.get("evidence"):
                    st.markdown("**📚 Supporting Evidence:**")

                    st.write(
                        accuracy["evidence"]
                    )

                # --------------------------------------------------
                # Hallucination
                # --------------------------------------------------

                st.subheader("🚨 Hallucination Detection")

                if hallucination["hallucination_detected"]:

                    st.error(
                        "Hallucination or unsupported claims detected."
                    )

                    flagged_claims = hallucination.get(
                        "flagged_claims",
                        []
                    )

                    for i, claim in enumerate(
                        flagged_claims,
                        start=1
                    ):

                        st.markdown(
                            f"### Claim {i}"
                        )

                        st.markdown(
                            f"**Claim:** {claim['claim']}"
                        )

                        st.markdown(
                            f"**Status:** {claim['status']}"
                        )

                        st.markdown(
                            f"**Reasoning:** {claim['reasoning']}"
                        )

                        st.markdown(
                            f"**Evidence:** {claim['evidence']}"
                        )

                else:

                    st.success(
                        "No unsupported or contradicted claims detected."
                    )

                # --------------------------------------------------
                # Overall Reasoning
                # --------------------------------------------------

                if hallucination.get("overall_reasoning"):

                    st.subheader(
                        "🧠 Hallucination Analysis"
                    )

                    st.write(
                        hallucination["overall_reasoning"]
                    )

            except Exception as e:

                st.error(
                    f"An error occurred: {str(e)}"
                )