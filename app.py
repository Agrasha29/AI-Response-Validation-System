import os
import subprocess
from datetime import datetime

import pandas as pd
import streamlit as st

from src.evaluation.orchestrator import EvaluationOrchestrator
from src.evaluation.batch_evaluator import BatchEvaluator
from src.reporting.pdf_report import (
    generate_single_evaluation_pdf,
    generate_batch_evaluation_pdf,
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Validation | Milestone 3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULT_STATE = {
    "single_result": None,
    "single_inputs": {},
    "batch_result": None,
    "batch_filename": None,
    "history": [],
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, dict) else ([] if isinstance(value, list) else value)


# ==========================================================
# PREMIUM UI
# ==========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #f6f7fb;
        --card: #ffffff;
        --text: #111827;
        --muted: #6b7280;
        --border: #e7e9f0;
        --primary: #635bff;
        --primary-dark: #5148e5;
        --success: #16a34a;
        --warning: #d97706;
        --danger: #dc2626;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(99,91,255,.08), transparent 25%),
            radial-gradient(circle at 10% 25%, rgba(124,58,237,.05), transparent 25%),
            var(--bg);
    }

    [data-testid="stHeader"] {
        background: rgba(246,247,251,.85);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #0f1020;
        border-right: 1px solid #20223a;
    }

    [data-testid="stSidebar"] * {
        color: #e9e9f2;
    }

    [data-testid="stSidebar"] .stRadio label {
        border-radius: 12px;
        padding: 8px 10px;
        transition: .2s ease;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,.07);
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 5px;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(99,91,255,.30), rgba(124,58,237,.18));
        border: 1px solid rgba(145,137,255,.28);
    }

    .brand {
        padding: 10px 4px 22px 4px;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: linear-gradient(135deg, #756cff, #8b5cf6);
        box-shadow: 0 12px 30px rgba(99,91,255,.25);
        font-size: 24px;
        margin-bottom: 12px;
    }

    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -.4px;
    }

    .brand-subtitle {
        color: #8f91a7;
        font-size: 12px;
        margin-top: 4px;
        line-height: 1.5;
    }

    .workspace-badge {
        display: inline-block;
        margin-top: 13px;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .7px;
        text-transform: uppercase;
        color: #c7c4ff;
        background: rgba(99,91,255,.14);
        border: 1px solid rgba(99,91,255,.25);
    }

    .page-kicker {
        color: var(--primary);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }

    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 34px;
        line-height: 1.15;
        font-weight: 700;
        letter-spacing: -1px;
        color: var(--text);
        margin-bottom: 7px;
    }

    .page-description {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 25px;
    }

    .hero {
        background: linear-gradient(135deg, #15162a 0%, #25265b 65%, #4d3ec8 100%);
        border-radius: 22px;
        padding: 28px 30px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 18px 50px rgba(35,32,84,.18);
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: '';
        position: absolute;
        width: 250px;
        height: 250px;
        right: -60px;
        top: -90px;
        border-radius: 50%;
        background: rgba(255,255,255,.08);
    }

    .hero h2 {
        font-family: 'Space Grotesk', sans-serif;
        margin: 0 0 7px 0;
        font-size: 27px;
        position: relative;
        z-index: 1;
    }

    .hero p {
        margin: 0;
        color: #c9cae3;
        max-width: 720px;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }

    .hero-chip {
        display: inline-block;
        margin-top: 17px;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(255,255,255,.10);
        border: 1px solid rgba(255,255,255,.12);
        font-size: 11px;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 7px 25px rgba(17,24,39,.035);
    }

    .card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 5px;
    }

    .card-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 16px;
    }

    .kpi {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 17px;
        padding: 18px;
        min-height: 108px;
        box-shadow: 0 7px 25px rgba(17,24,39,.035);
    }

    .kpi-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
    }

    .kpi-value {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 27px;
        font-weight: 700;
        margin-top: 8px;
    }

    .kpi-note {
        color: #8b8fa1;
        font-size: 11px;
        margin-top: 4px;
    }

    .verdict-pass, .verdict-needs, .verdict-fail {
        border-radius: 18px;
        padding: 20px 22px;
        margin: 10px 0 18px 0;
        border: 1px solid;
    }

    .verdict-pass { background: #f0fdf4; border-color: #bbf7d0; }
    .verdict-needs { background: #fffbeb; border-color: #fde68a; }
    .verdict-fail { background: #fef2f2; border-color: #fecaca; }

    .verdict-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 700;
    }

    .score-pill {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        background: #f1f2f8;
        color: #374151;
        font-size: 11px;
        font-weight: 700;
    }

    .section-divider {
        height: 1px;
        background: var(--border);
        margin: 28px 0;
    }

    div.stButton > button {
        border-radius: 11px;
        border: 1px solid #dcddea;
        font-weight: 700;
        min-height: 43px;
        transition: .2s ease;
    }

    div.stButton > button:hover {
        border-color: #aaa5ff;
        transform: translateY(-1px);
        box-shadow: 0 7px 20px rgba(99,91,255,.12);
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #635bff, #7c3aed);
        border: none;
        color: white;
    }

    .footer {
        margin-top: 45px;
        padding-top: 18px;
        border-top: 1px solid var(--border);
        color: #8b8fa1;
        text-align: center;
        font-size: 11px;
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        margin-right: 6px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================

def make_display_safe(value):
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(str(make_display_safe(item)) for item in value)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {make_display_safe(val)}" for key, val in value.items())
    return str(value)


def make_dataframe_display_safe(df):
    display_df = df.copy()
    for column in display_df.columns:
        display_df[column] = display_df[column].apply(make_display_safe)
    return display_df


def page_header(kicker, title, description):
    st.markdown(f'<div class="page-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-description">{description}</div>', unsafe_allow_html=True)


def kpi(label, value, note=""):
    st.markdown(
        f'''<div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>''',
        unsafe_allow_html=True,
    )


def section_title(title, subtitle=""):
    st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="card-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_verdict(verdict):
    value = verdict.get("verdict", "Unknown")
    score = float(verdict.get("overall_score", 0) or 0)
    if value == "Pass":
        cls, icon = "verdict-pass", "✓"
    elif value == "Needs Improvement":
        cls, icon = "verdict-needs", "!"
    else:
        cls, icon = "verdict-fail", "×"

    st.markdown(
        f'''<div class="{cls}">
            <div style="font-size:12px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:1px;">Final Verdict</div>
            <div class="verdict-label">{icon} {value}</div>
            <div style="margin-top:5px;color:#6b7280;font-size:13px;">Weighted overall quality score: <b>{score:.2f}/5</b></div>
        </div>''',
        unsafe_allow_html=True,
    )


def add_history_entry(result, source="Single Evaluation"):
    verdict = result.get("verdict", {})
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": source,
        "question": result.get("question", ""),
        "score": float(verdict.get("overall_score", 0) or 0),
        "verdict": verdict.get("verdict", "Unknown"),
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:100]


def successful_results(batch_result):
    return [
        item for item in batch_result.results
        if item.get("verdict") in {"Pass", "Needs Improvement", "Fail"}
    ]


def render_batch_dashboard(batch_result):
    stats = batch_result.statistics
    results = successful_results(batch_result)
    total = batch_result.total_rows
    successful = batch_result.successful_rows
    failed = batch_result.failed_rows

    pass_count = sum(item.get("verdict") == "Pass" for item in results)
    needs_count = sum(item.get("verdict") == "Needs Improvement" for item in results)
    fail_count = sum(item.get("verdict") == "Fail" for item in results)
    pass_rate = pass_count / successful * 100 if successful else 0
    hallucination_count = sum(bool(item.get("hallucination_detected")) for item in results)
    hallucination_rate = hallucination_count / successful * 100 if successful else 0

    st.markdown("### Overview")
    cols = st.columns(5)
    values = [
        ("Total Responses", total, "Uploaded records"),
        ("Successful", successful, "Completed evaluations"),
        ("Failed", failed, "Evaluation errors"),
        ("Pass Rate", f"{pass_rate:.1f}%", "Among successful evaluations"),
        ("Average Quality", f"{stats.get('average_overall_score', 0):.2f}/5", "Weighted score"),
    ]
    for col, (label, value, note) in zip(cols, values):
        with col:
            kpi(label, value, note)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Verdict Distribution", "Pass, Needs Improvement and Fail rates")
        verdict_df = pd.DataFrame({
            "Verdict": ["Pass", "Needs Improvement", "Fail"],
            "Rate (%)": [
                pass_count / successful * 100 if successful else 0,
                needs_count / successful * 100 if successful else 0,
                fail_count / successful * 100 if successful else 0,
            ],
        })
        st.bar_chart(verdict_df.set_index("Verdict"))
        st.dataframe(verdict_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Dimension Quality", "Average score across the four evaluation dimensions")
        dimension_df = pd.DataFrame({
            "Dimension": ["Relevance", "Accuracy", "Completeness", "Hallucination"],
            "Average Score": [
                stats.get("average_relevance", 0),
                stats.get("average_accuracy", 0),
                stats.get("average_completeness", 0),
                stats.get("average_hallucination", 0),
            ],
        })
        st.bar_chart(dimension_df.set_index("Dimension"))
        st.dataframe(dimension_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Quality Indicators")
    cols = st.columns(5)
    quality = [
        ("Avg Relevance", f"{stats.get('average_relevance', 0):.2f}/5", "Response relevance"),
        ("Avg Accuracy", f"{stats.get('average_accuracy', 0):.2f}/5", "Factual correctness"),
        ("Avg Completeness", f"{stats.get('average_completeness', 0):.2f}/5", "Requirement coverage"),
        ("Avg Hallucination", f"{stats.get('average_hallucination', 0):.2f}/5", "5 = no hallucination"),
        ("Hallucination Rate", f"{hallucination_rate:.1f}%", "Detected in successful rows"),
    ]
    for col, (label, value, note) in zip(cols, quality):
        with col:
            kpi(label, value, note)

    st.markdown("### Quality Trend — Current Batch")
    if results:
        trend_rows = []
        for index, item in enumerate(results, start=1):
            trend_rows.append({
                "Response": index,
                "Overall Score": float(item.get("overall_score", 0) or 0),
                "Relevance": float(item.get("relevance_score", 0) or 0),
                "Accuracy": float(item.get("accuracy_score", 0) or 0),
                "Completeness": float(item.get("completeness_score", 0) or 0),
                "Hallucination": float(item.get("hallucination_score", 0) or 0),
            })
        st.line_chart(pd.DataFrame(trend_rows).set_index("Response"))
        st.caption("Trend follows successful responses in the uploaded CSV. Historical cross-batch trends require persistent storage.")
    else:
        st.info("No successful evaluations available for trend analysis.")


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

with st.sidebar:
    st.markdown(
        '''<div class="brand">
            <div class="brand-icon">🤖</div>
            <div class="brand-title">AI Validation</div>
            <div class="brand-subtitle">AI Response Validation & Quality Assurance Platform</div>
            <div class="workspace-badge">Milestone 4 Workspace</div>
        </div>''',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='color:#686b82;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin:10px 8px 7px;'>Workspace</div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🧪 Single Evaluation",
            "📂 Batch Evaluation",
            "🕘 Evaluation History",
            "📚 Knowledge Base",
            "🧪 Testing / System Status",
            "ℹ️ About Project",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#7f8299;font-size:11px;line-height:1.6;padding:0 8px;">'
        '<span class="status-dot"></span>Local application ready<br>'
        'Gemini-powered multi-agent evaluation'
        '</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# DASHBOARD
# ==========================================================
# ==========================================================
# DASHBOARD
# ==========================================================

if page == "🏠 Dashboard":
    page_header(
        "AI Quality Assurance",
        "Dashboard",
        "Monitor evaluation performance, verdicts, quality scores and hallucination trends.",
    )

    # ======================================================
    # CALCULATE OVERALL SESSION STATISTICS
    # ======================================================

    history = st.session_state.history

    total_evaluations = len(history)

    pass_count = sum(
        1 for item in history
        if item.get("verdict") == "Pass"
    )

    needs_improvement_count = sum(
        1 for item in history
        if item.get("verdict") == "Needs Improvement"
    )

    fail_count = sum(
        1 for item in history
        if item.get("verdict") == "Fail"
    )

    evaluation_error_count = sum(
        1 for item in history
        if item.get("verdict") == "Evaluation Error"
    )

    successful_evaluations = (
        pass_count
        + needs_improvement_count
        + fail_count
    )

    pass_rate = (
        (pass_count / successful_evaluations) * 100
        if successful_evaluations
        else 0
    )

    average_score = (
        sum(float(item.get("score", 0) or 0) for item in history)
        / successful_evaluations
        if successful_evaluations
        else 0
    )

    # ======================================================
    # HERO
    # ======================================================

    st.markdown(
        f'''<div class="hero">
            <h2>AI Evaluation Overview</h2>
            <p>
                Track all response evaluations performed during the current
                Streamlit session. Monitor verdicts, quality scores and
                evaluation performance from one place.
            </p>
            <div class="hero-chip">
                📊 {total_evaluations} total evaluation(s)
            </div>
        </div>''',
        unsafe_allow_html=True,
    )

    # ======================================================
    # MAIN KPI CARDS
    # ======================================================

    st.markdown("### 📊 Evaluation Overview")

    cols = st.columns(6)

    dashboard_kpis = [
        (
            "Total Evaluations",
            total_evaluations,
            "All evaluations"
        ),
        (
            "Passed",
            pass_count,
            "Successful responses"
        ),
        (
            "Needs Improvement",
            needs_improvement_count,
            "Responses requiring review"
        ),
        (
            "Failed",
            fail_count,
            "Unsuccessful responses"
        ),
        (
            "Pass Rate",
            f"{pass_rate:.1f}%",
            "Among completed evaluations"
        ),
        (
            "Average Score",
            f"{average_score:.2f}/5",
            "Overall quality"
        ),
    ]

    for col, (label, value, note) in zip(cols, dashboard_kpis):
        with col:
            kpi(label, value, note)

    # ======================================================
    # SECONDARY STATISTICS
    # ======================================================

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Evaluation Statistics")

    cols = st.columns(4)

    secondary_kpis = [
        (
            "Successful Evaluations",
            successful_evaluations,
            "Pass + Needs Improvement + Fail"
        ),
        (
            "Evaluation Errors",
            evaluation_error_count,
            "Failed evaluation processes"
        ),
        (
            "Highest Score",
            (
                f"{max(float(item.get('score', 0) or 0) for item in history):.2f}/5"
                if history else "0.00/5"
            ),
            "Best evaluation"
        ),
        (
            "Lowest Score",
            (
                f"{min(float(item.get('score', 0) or 0) for item in history):.2f}/5"
                if history else "0.00/5"
            ),
            "Lowest evaluation"
        ),
    ]

    for col, (label, value, note) in zip(cols, secondary_kpis):
        with col:
            kpi(label, value, note)

    # ======================================================
    # EMPTY STATE
    # ======================================================

    if not history:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        st.markdown(
            '''<div class="card">
                <div class="card-title">🚀 No evaluations yet</div>
                <div class="card-subtitle">
                    Start with Single Evaluation or Batch Evaluation.
                    Your evaluation statistics will automatically appear
                    here after the first evaluation is completed.
                </div>
            </div>''',
            unsafe_allow_html=True,
        )

    else:

        # ==================================================
        # VERDICT DISTRIBUTION
        # ==================================================

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        left, right = st.columns(2)

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            section_title(
                "Verdict Distribution",
                "Overall evaluation outcomes"
            )

            verdict_df = pd.DataFrame({
                "Verdict": [
                    "Pass",
                    "Needs Improvement",
                    "Fail",
                ],
                "Evaluations": [
                    pass_count,
                    needs_improvement_count,
                    fail_count,
                ],
            })

            st.bar_chart(
                verdict_df.set_index("Verdict")
            )

            st.dataframe(
                verdict_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SCORE DISTRIBUTION
        # ==================================================

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            section_title(
                "Score Overview",
                "Average score across evaluations"
            )

            score_data = pd.DataFrame({
                "Evaluation": range(1, len(history) + 1),
                "Score": [
                    float(item.get("score", 0) or 0)
                    for item in reversed(history)
                ],
            })

            st.line_chart(
                score_data.set_index("Evaluation")
            )

            st.caption(
                "Scores are shown from oldest to newest evaluation."
            )

            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # RECENT EVALUATIONS
        # ==================================================

        st.markdown("### 🕘 Recent Evaluations")

        recent_history = history[:10]

        recent_df = pd.DataFrame(recent_history)

        if not recent_df.empty:

            recent_df.insert(
                0,
                "#",
                range(1, len(recent_df) + 1)
            )

            recent_df = recent_df.rename(
                columns={
                    "time": "Date / Time",
                    "source": "Mode",
                    "question": "Question",
                    "score": "Score",
                    "verdict": "Verdict",
                }
            )

            recent_df["Score"] = recent_df["Score"].apply(
                lambda value: f"{float(value):.2f}/5"
            )

            st.dataframe(
                recent_df[
                    [
                        "#",
                        "Date / Time",
                        "Mode",
                        "Question",
                        "Score",
                        "Verdict",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        # ==================================================
        # PERFORMANCE SUMMARY
        # ==================================================

        st.markdown("### 🎯 Performance Summary")

        summary_left, summary_right = st.columns(2)

        with summary_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            section_title(
                "Evaluation Breakdown",
                "Current session statistics"
            )

            st.write(
                f"**Total evaluations:** {total_evaluations}"
            )

            st.write(
                f"**Successful evaluations:** {successful_evaluations}"
            )

            st.write(
                f"**Passed:** {pass_count}"
            )

            st.write(
                f"**Needs Improvement:** {needs_improvement_count}"
            )

            st.write(
                f"**Failed:** {fail_count}"
            )

            if evaluation_error_count:
                st.write(
                    f"**Evaluation errors:** {evaluation_error_count}"
                )

            st.markdown('</div>', unsafe_allow_html=True)

        with summary_right:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            section_title(
                "Quality Summary",
                "Overall response quality"
            )

            st.write(
                f"**Average score:** {average_score:.2f}/5"
            )

            st.write(
                f"**Pass rate:** {pass_rate:.1f}%"
            )

            if history:
                highest_score = max(
                    float(item.get("score", 0) or 0)
                    for item in history
                )

                lowest_score = min(
                    float(item.get("score", 0) or 0)
                    for item in history
                )

                st.write(
                    f"**Highest score:** {highest_score:.2f}/5"
                )

                st.write(
                    f"**Lowest score:** {lowest_score:.2f}/5"
                )

            st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # LATEST BATCH DETAILS
    # ======================================================

    if st.session_state.batch_result is not None:

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        batch = st.session_state.batch_result

        st.markdown("### 📂 Latest Batch Evaluation")

        batch_cols = st.columns(5)

        batch_values = [
            (
                "Batch Records",
                batch.total_rows,
                "Uploaded records"
            ),
            (
                "Successful",
                batch.successful_rows,
                "Completed evaluations"
            ),
            (
                "Failed",
                batch.failed_rows,
                "Evaluation errors"
            ),
            (
                "Batch Score",
                f"{batch.statistics.get('average_overall_score', 0):.2f}/5",
                "Average quality"
            ),
            (
                "Batch File",
                st.session_state.batch_filename or "CSV",
                "Latest dataset"
            ),
        ]

        for col, (label, value, note) in zip(
            batch_cols,
            batch_values
        ):
            with col:
                kpi(label, value, note)

    # ======================================================
    # FOOTNOTE
    # ======================================================

    st.caption(
        "ℹ️ Dashboard statistics are based on evaluations recorded "
        "during the current Streamlit session. Restarting the application "
        "clears the session history."
    )




# ==========================================================
# SINGLE EVALUATION
# ==========================================================

elif page == "🧪 Single Evaluation":
    page_header(
        "Response Analysis",
        "Single Evaluation",
        "Evaluate one AI response through the complete multi-agent validation pipeline.",
    )

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Evaluation Input", "Provide the question, AI response and optional grounding information.")

        question = st.text_area(
            "Question",
            value=st.session_state.single_inputs.get("question", ""),
            placeholder="Enter the user's question...",
            height=120,
            key="single_question",
        )
        response = st.text_area(
            "AI Response",
            value=st.session_state.single_inputs.get("response", ""),
            placeholder="Enter the AI-generated response...",
            height=180,
            key="single_response",
        )
        reference_answer = st.text_area(
            "Reference Answer · Optional",
            value=st.session_state.single_inputs.get("reference_answer", ""),
            placeholder="Provide a trusted reference answer when available...",
            height=110,
            key="single_reference",
        )
        source_context = st.text_area(
            "Source Context · Optional",
            value=st.session_state.single_inputs.get("source_context", ""),
            placeholder="Provide source context for grounded accuracy/hallucination evaluation...",
            height=110,
            key="single_source",
        )

        evaluate_clicked = st.button("🚀 Evaluate Response", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Evaluation Pipeline", "The orchestrator sends the response through four judges and the final verdict layer.")
        st.markdown(
            """
            **1 · 🔎 Relevance Judge**  
            Measures how directly the response addresses the question.

            **2 · 🎯 Accuracy Judge**  
            Checks factual correctness against references or source context.

            **3 · 🚨 Hallucination Detector**  
            Identifies unsupported or contradicted claims.

            **4 · 🧩 Completeness Judge**  
            Checks whether important requirements are addressed.

            **5 · ⚖️ Verdict Agent**  
            Combines the four dimensions using the project's weighted scoring model.
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if evaluate_clicked:
        if not question.strip():
            st.error("Please enter a question.")
        elif not response.strip():
            st.error("Please enter an AI response.")
        else:
            with st.spinner("Running the evaluation agents..."):
                try:
                    result = EvaluationOrchestrator().evaluate(
                        question=question,
                        response=response,
                        reference_answer=reference_answer,
                        source_context=source_context,
                    )
                    st.session_state.single_result = result
                    st.session_state.single_inputs = {
                        "question": question,
                        "response": response,
                        "reference_answer": reference_answer,
                        "source_context": source_context,
                    }
                    add_history_entry(result)
                    st.success("Evaluation completed successfully.")
                except Exception as error:
                    st.error(f"Evaluation failed: {error}")

    result = st.session_state.single_result
    if result:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        page_header("Evaluation Output", "Response Quality Report", "Scores and reasoning from every evaluation dimension.")

        relevance = result["relevance"]
        accuracy = result["accuracy"]
        hallucination = result["hallucination"]
        completeness = result["completeness"]
        verdict = result["verdict"]

        cols = st.columns(5)
        score_cards = [
            ("Relevance", float(relevance.get("relevance_score", 0)), "Question alignment"),
            ("Accuracy", float(accuracy.get("accuracy_score", 0)), "Factual correctness"),
            ("Completeness", float(completeness.get("completeness_score", 0)), "Requirement coverage"),
            ("Hallucination", 1 if hallucination.get("hallucination_detected") else 5, "5 = no hallucination"),
            ("Overall", float(verdict.get("overall_score", 0)), "Weighted verdict score"),
        ]
        for col, (label, value, note) in zip(cols, score_cards):
            with col:
                kpi(label, f"{value:.1f}/5", note)

        render_verdict(verdict)

        major_issues = verdict.get("major_issues", [])
        if major_issues:
            st.warning("**Major issues detected:**\n\n" + "\n".join(f"- {make_display_safe(x)}" for x in major_issues))

        st.markdown("### Agent Analysis")
        a, b = st.columns(2)
        with a:
            with st.expander("🔎 Relevance Judge", expanded=False):
                st.write(f"**Score:** {relevance.get('relevance_score', 0)}/5")
                st.write(relevance.get("reasoning", ""))
            with st.expander("🎯 Accuracy Judge", expanded=False):
                st.write(f"**Score:** {accuracy.get('accuracy_score', 0)}/5")
                st.write(accuracy.get("reasoning", ""))
                if accuracy.get("evidence"):
                    st.write("**Evidence**")
                    st.write(make_display_safe(accuracy["evidence"]))
        with b:
            with st.expander("🧩 Completeness Judge", expanded=False):
                st.write(f"**Score:** {completeness.get('completeness_score', 0)}/5")
                st.write(completeness.get("reasoning", ""))
                if completeness.get("addressed_aspects"):
                    st.write("**Addressed**")
                    for item in completeness["addressed_aspects"]:
                        st.write(f"✅ {make_display_safe(item)}")
                if completeness.get("partial_aspects"):
                    st.write("**Partial**")
                    for item in completeness["partial_aspects"]:
                        st.write(f"🟡 {make_display_safe(item)}")
                if completeness.get("missing_aspects"):
                    st.write("**Missing**")
                    for item in completeness["missing_aspects"]:
                        st.write(f"❌ {make_display_safe(item)}")
            with st.expander("🚨 Hallucination Detector", expanded=False):
                detected = hallucination.get("hallucination_detected", False)
                if detected:
                    st.error("❌ Hallucination detected")
                else:
                    st.success("✅ No hallucination detected")
                for claim in hallucination.get("flagged_claims", []):
                    if isinstance(claim, dict):
                        st.markdown(f"**Claim:** {make_display_safe(claim.get('claim', ''))}")
                        st.write(f"**Status:** {make_display_safe(claim.get('status', ''))}")
                        st.write(f"**Reasoning:** {make_display_safe(claim.get('reasoning', ''))}")
                        if claim.get("evidence"):
                            st.write(f"**Evidence:** {make_display_safe(claim.get('evidence'))}")
                    else:
                        st.write(make_display_safe(claim))
                st.write("**Overall reasoning**")
                st.write(hallucination.get("overall_reasoning", ""))

        with st.expander("🧠 Consolidated Verdict Reasoning", expanded=False):
            st.write(verdict.get("reasoning", ""))

        st.markdown("### PDF Export")
        pdf_payload = dict(result)
        pdf_payload["reference_answer"] = st.session_state.single_inputs.get("reference_answer", "")
        pdf_payload["source_context"] = st.session_state.single_inputs.get("source_context", "")
        pdf_file = generate_single_evaluation_pdf(pdf_payload)
        st.download_button(
            "📥 Download Single Evaluation PDF",
            data=pdf_file,
            file_name="ai_response_evaluation_report.pdf",
            mime="application/pdf",
            key="download_single_pdf",
        )


# ==========================================================
# BATCH EVALUATION
# ==========================================================

elif page == "📂 Batch Evaluation":
    page_header(
        "Multi-response Analysis",
        "Batch Evaluation",
        "Upload a CSV dataset, validate its structure, evaluate all records and inspect the scoring dashboard.",
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_title("Upload Evaluation Dataset", "Required: question, ai_response · Optional: reference_answer, source_context")
    uploaded_file = st.file_uploader("Drop your CSV here", type=["csv"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            evaluator = BatchEvaluator()

            try:
                evaluator.validate_dataframe(df)
                st.success(f"CSV structure is valid — {len(df)} record(s) found.")
            except ValueError as validation_error:
                st.error(str(validation_error))
                st.stop()

            with st.expander("👀 Preview uploaded data", expanded=True):
                st.dataframe(make_dataframe_display_safe(df), use_container_width=True, hide_index=True)

            st.info(f"Ready to process {len(df)} record(s). The batch evaluator sends the complete batch through the batch evaluation pipeline.")

            if st.button("🚀 Run Batch Evaluation", type="primary", use_container_width=True):
                progress = st.progress(0)
                status = st.empty()
                status.info(f"Evaluating {len(df)} record(s)...")
                try:
                    batch_result = evaluator.evaluate_dataframe(df)
                    progress.progress(100)
                    status.success("Batch evaluation completed successfully.")
                    st.session_state.batch_result = batch_result
                    st.session_state.batch_filename = uploaded_file.name

                    for item in successful_results(batch_result):
                        entry = {
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "source": "Batch Evaluation",
                            "question": item.get("question", ""),
                            "score": float(item.get("overall_score", 0) or 0),
                            "verdict": item.get("verdict", "Unknown"),
                        }
                        st.session_state.history.insert(0, entry)
                    st.session_state.history = st.session_state.history[:100]
                except Exception as error:
                    progress.progress(100)
                    status.error("Batch evaluation failed.")
                    st.error(f"Batch evaluation failed: {error}")

        except Exception as error:
            st.error(f"Could not read CSV file: {error}")

    batch_result = st.session_state.batch_result
    if batch_result is not None:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        page_header("Milestone 4 Dashboard", "Evaluation Scoring Dashboard", "Visual summary of the latest batch evaluation.")
        render_batch_dashboard(batch_result)

        st.markdown("### Detailed Evaluation Results")
        if batch_result.results:
            results_df = pd.DataFrame(batch_result.results)
            st.dataframe(make_dataframe_display_safe(results_df), use_container_width=True, hide_index=True)
        else:
            st.warning("No evaluation results were generated.")

        failed_results = [item for item in batch_result.results if item.get("verdict") == "Evaluation Error"]
        if failed_results:
            st.markdown("### Failed Evaluations")
            st.dataframe(make_dataframe_display_safe(pd.DataFrame(failed_results)), use_container_width=True, hide_index=True)

        st.markdown("### PDF Export")
        batch_pdf_payload = {
            "total_rows": batch_result.total_rows,
            "successful_rows": batch_result.successful_rows,
            "failed_rows": batch_result.failed_rows,
            "statistics": batch_result.statistics,
            "results": batch_result.results,
        }
        batch_pdf_file = generate_batch_evaluation_pdf(batch_pdf_payload)
        st.download_button(
            "📥 Download Batch PDF Report",
            data=batch_pdf_file,
            file_name="batch_ai_response_evaluation_report.pdf",
            mime="application/pdf",
            key="download_batch_pdf_report",
        )


# ==========================================================
# EVALUATION HISTORY
# ==========================================================

elif page == "🕘 Evaluation History":
    page_header(
        "Session Records",
        "Evaluation History",
        "Review evaluations completed during the current Streamlit session.",
    )

    if not st.session_state.history:
        st.info("No evaluations have been recorded in this session yet. Run a single or batch evaluation first.")
    else:
        history_df = pd.DataFrame(st.session_state.history)
        history_df.insert(0, "#", range(1, len(history_df) + 1))
        history_df = history_df.rename(columns={
            "time": "Date / Time",
            "source": "Mode",
            "question": "Question",
            "score": "Score",
            "verdict": "Verdict",
        })
        history_df["Score"] = history_df["Score"].map(lambda x: f"{float(x):.2f}/5")
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        st.caption("History is session-based. Restarting Streamlit clears this temporary history unless persistent storage is added.")


# ==========================================================
# KNOWLEDGE BASE
# ==========================================================

elif page == "📚 Knowledge Base":
    page_header(
        "Grounding Resources",
        "Knowledge Base",
        "Inspect the benchmark/reference resources used to support grounded evaluation and retrieval.",
    )

    candidates = [
        "data/benchmark_questions.json",
        "data/README.md",
    ]
    existing = [(path, os.path.getsize(path)) for path in candidates if os.path.exists(path)]

    cols = st.columns(3)
    with cols[0]:
        kpi("Resource Files", len(existing), "Detected in project")
    with cols[1]:
        kpi("Retrieval", "TF-IDF", "Current retriever implementation")
    with cols[2]:
        kpi("Grounding", "RAG", "Reference/source-assisted evaluation")

    st.markdown("### Available Resources")
    if existing:
        for path, size in existing:
            st.markdown(
                f'''<div class="card" style="margin-bottom:10px;">
                    <div class="card-title">📄 {path}</div>
                    <div class="card-subtitle">{size:,} bytes</div>
                </div>''',
                unsafe_allow_html=True,
            )
            if path.endswith(".md"):
                try:
                    with st.expander(f"View {path}"):
                        with open(path, "r", encoding="utf-8") as handle:
                            st.markdown(handle.read())
                except Exception as error:
                    st.warning(f"Could not read {path}: {error}")
    else:
        st.info("No benchmark knowledge-base files were found at the expected project paths.")

    if os.path.exists("data/benchmark_questions.json"):
        try:
            import json
            with open("data/benchmark_questions.json", "r", encoding="utf-8") as handle:
                kb_data = json.load(handle)
            st.markdown("### Benchmark Preview")
            if isinstance(kb_data, list):
                st.write(f"Loaded {len(kb_data)} benchmark item(s).")
                preview = pd.DataFrame(kb_data[:10])
                st.dataframe(make_dataframe_display_safe(preview), use_container_width=True, hide_index=True)
            else:
                st.json(kb_data)
        except Exception as error:
            st.warning(f"Could not parse benchmark_questions.json: {error}")


# ==========================================================
# TESTING / SYSTEM STATUS
# ==========================================================

elif page == "🧪 Testing / System Status":
    page_header(
        "Reliability & Validation",
        "Testing / System Status",
        "Check the availability of core modules and review the project's end-to-end test status.",
    )

    modules = [
        ("Relevance Judge", "src.agents.relevance_judge"),
        ("Accuracy Judge", "src.agents.accuracy_judge"),
        ("Hallucination Detector", "src.agents.hallucination_detector"),
        ("Completeness Judge", "src.agents.completeness_judge"),
        ("Verdict Agent", "src.agents.verdict_agent"),
        ("Batch Evaluator", "src.evaluation.batch_evaluator"),
        ("Orchestrator", "src.evaluation.orchestrator"),
        ("PDF Reporting", "src.reporting.pdf_report"),
    ]

    rows = []
    for label, module_name in modules:
        try:
            __import__(module_name)
            status = "🟢 Ready"
        except Exception as error:
            status = f"🔴 Error: {error}"
        rows.append({"Component": label, "Status": status})

    st.markdown("### Component Health")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### End-to-End Test Status")
    test_path = "tests/test_m4_end_to_end.py"
    if os.path.exists(test_path):
        st.info("The project contains the M4 end-to-end test suite. The validated project state recorded during development was **8/8 tests passed (100%)**.")
        st.code("python -m pytest -q tests/test_m4_end_to_end.py", language="powershell")
    else:
        st.warning("tests/test_m4_end_to_end.py was not found in the current working directory.")

    st.markdown("### Runtime")
    runtime_cols = st.columns(3)
    with runtime_cols[0]:
        kpi("Python", f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}", "Current interpreter")
    with runtime_cols[1]:
        kpi("Streamlit", "Active", "Application runtime")
    with runtime_cols[2]:
        kpi("LLM Client", "Gemini", "Configured by project")


# ==========================================================
# ABOUT PROJECT
# ==========================================================

else:
    page_header(
        "Project Information",
        "About Project",
        "Development workspace for the AI Response Validation System — Milestone 3 / Milestone 4 implementation.",
    )

    st.markdown(
        '''<div class="hero">
            <h2>AI Response Validation System</h2>
            <p>A multi-agent evaluation platform for assessing AI-generated responses across relevance, factual accuracy, hallucination risk and completeness, followed by a weighted final verdict.</p>
            <div class="hero-chip">🎓 Infosys Springboard Internship · Batch 3 · 2026–27</div>
        </div>''',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Evaluation Architecture", "Core pipeline")
        st.markdown(
            """
            **Question + AI Response**  
            ↓  
            **Reference / Source Context / Retrieval**  
            ↓  
            **Relevance · Accuracy · Hallucination · Completeness**  
            ↓  
            **Weighted Verdict Agent**  
            ↓  
            **Dashboard + PDF Report**
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        section_title("Technology Stack", "Current implementation")
        st.markdown(
            """
            - **Python** — application and evaluation logic
            - **Streamlit** — interactive dashboard
            - **Gemini** — structured LLM evaluation
            - **Pydantic** — structured agent outputs
            - **Pandas** — batch CSV processing
            - **Scikit-learn** — TF-IDF retrieval
            - **ReportLab** — PDF report generation
            - **Pytest** — end-to-end validation
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Evaluation Dimensions")
    cols = st.columns(4)
    dimensions = [
        ("🔎", "Relevance", "25%", "Question alignment"),
        ("🎯", "Accuracy", "30%", "Factual correctness"),
        ("🧩", "Completeness", "25%", "Requirement coverage"),
        ("🚨", "Hallucination", "20%", "Unsupported claims"),
    ]
    for col, (icon, name, weight, desc) in zip(cols, dimensions):
        with col:
            st.markdown(
                f'''<div class="card">
                    <div style="font-size:23px">{icon}</div>
                    <div class="card-title" style="margin-top:8px">{name}</div>
                    <div class="score-pill">Weight {weight}</div>
                    <div class="card-subtitle" style="margin-top:10px;margin-bottom:0">{desc}</div>
                </div>''',
                unsafe_allow_html=True,
            )

    st.markdown("### Verdict Rules")
    verdict_rules = pd.DataFrame({
        "Overall Score": ["4.0 – 5.0", "2.5 – 3.99", "1.0 – 2.49"],
        "Verdict": ["Pass", "Needs Improvement", "Fail"],
        "Critical Failure": ["No", "No", "No"],
    })
    st.dataframe(verdict_rules, use_container_width=True, hide_index=True)
    st.caption("Critical failure rules also force Fail when accuracy score is 1 or hallucination is detected, as implemented by the Verdict Agent.")


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    '<div class="footer">AI Response Validation System · Milestone 3 Workspace · Multi-Agent Evaluation Platform</div>',
    unsafe_allow_html=True,
)