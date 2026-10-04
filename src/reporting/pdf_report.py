from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _safe(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple)):
        return "; ".join(_safe(v) for v in value)
    if isinstance(value, dict):
        return "; ".join(f"{k}: {_safe(v)}" for k, v in value.items())
    return str(value)


def _paragraph(text, style):
    return Paragraph(escape(_safe(text)).replace("\n", "<br/>").replace("  ", " &nbsp;"), style)


def _recommendations(stats, results):
    recommendations = []
    dimensions = {
        "Relevance": float(stats.get("average_relevance", 0) or 0),
        "Accuracy": float(stats.get("average_accuracy", 0) or 0),
        "Completeness": float(stats.get("average_completeness", 0) or 0),
        "Hallucination": float(stats.get("average_hallucination", 0) or 0),
    }

    if dimensions["Accuracy"] < 4:
        recommendations.append("Improve factual accuracy by grounding answers in verified reference answers or retrieved source evidence.")
    if dimensions["Completeness"] < 4:
        recommendations.append("Improve completeness by explicitly covering all important requirements and sub-questions before finalizing a response.")
    if dimensions["Relevance"] < 4:
        recommendations.append("Improve relevance by focusing directly on the user's question and removing unrelated information.")
    if dimensions["Hallucination"] < 4:
        recommendations.append("Reduce hallucinations by verifying claims against available source context and avoiding unsupported assertions.")

    hallucinations = sum(
        1 for r in results
        if r.get("verdict") in {"Pass", "Needs Improvement", "Fail"}
        and bool(r.get("hallucination_detected"))
    )
    if hallucinations:
        recommendations.append(f"Review the {hallucinations} response(s) with detected hallucinations and validate each flagged claim against evidence.")

    failures = sum(1 for r in results if r.get("verdict") == "Fail")
    if failures:
        recommendations.append(f"Prioritize manual review of the {failures} failed evaluation(s), especially cases involving critical accuracy or hallucination issues.")

    if not recommendations:
        recommendations.append("Maintain the current evaluation quality and continue monitoring new batches for regressions in accuracy, completeness, relevance, and hallucination rate.")

    return recommendations


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
        fontSize=20, leading=24, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading2"], fontSize=13, leading=16,
        spaceBefore=10, spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11
    ))
    styles.add(ParagraphStyle(
        name="BodySafe", parent=styles["BodyText"], fontSize=9.5, leading=13
    ))
    return styles


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(15 * mm, 10 * mm, "AI Response Validation System")
    canvas.drawRightString(195 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def generate_batch_evaluation_pdf(batch_payload):
    """Generate a structured PDF report for a completed batch evaluation."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15 * mm, leftMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=17 * mm
    )
    styles = _build_styles()
    story = []

    total_rows = int(batch_payload.get("total_rows", 0) or 0)
    successful_rows = int(batch_payload.get("successful_rows", 0) or 0)
    failed_rows = int(batch_payload.get("failed_rows", 0) or 0)
    stats = batch_payload.get("statistics", {}) or {}
    results = batch_payload.get("results", []) or []

    valid_results = [
        r for r in results
        if r.get("verdict") in {"Pass", "Needs Improvement", "Fail"}
    ]
    denominator = len(valid_results)
    pass_count = sum(r.get("verdict") == "Pass" for r in valid_results)
    needs_count = sum(r.get("verdict") == "Needs Improvement" for r in valid_results)
    fail_count = sum(r.get("verdict") == "Fail" for r in valid_results)
    hallucination_count = sum(bool(r.get("hallucination_detected")) for r in valid_results)

    story.append(Paragraph("AI Response Validation System", styles["ReportTitle"]))
    story.append(Paragraph("Batch Evaluation Report", styles["Title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(_paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Small"]
    ))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("1. Batch Summary", styles["Section"]))
    summary = [
        ["Metric", "Value"],
        ["Total responses", str(total_rows)],
        ["Successful evaluations", str(successful_rows)],
        ["Failed evaluations", str(failed_rows)],
        ["Pass rate", f"{(pass_count / denominator * 100) if denominator else 0:.1f}%"],
        ["Needs Improvement", str(needs_count)],
        ["Fail", str(fail_count)],
        ["Average overall score", f"{float(stats.get('average_overall_score', 0) or 0):.2f}/5"],
        ["Hallucination frequency", f"{hallucination_count} ({(hallucination_count / denominator * 100) if denominator else 0:.1f}%)"],
    ]
    table = Table(summary, colWidths=[80 * mm, 85 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f3f4f6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("2. Dimension Breakdown", styles["Section"]))
    dimension_rows = [
        ["Dimension", "Average Score / 5"],
        ["Relevance", f"{float(stats.get('average_relevance', 0) or 0):.2f}"],
        ["Accuracy", f"{float(stats.get('average_accuracy', 0) or 0):.2f}"],
        ["Completeness", f"{float(stats.get('average_completeness', 0) or 0):.2f}"],
        ["Hallucination", f"{float(stats.get('average_hallucination', 0) or 0):.2f}"],
    ]
    dt = Table(dimension_rows, colWidths=[80 * mm, 85 * mm], repeatRows=1)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(dt)

    story.append(Paragraph("3. Flagged Responses", styles["Section"]))
    flagged = [
        r for r in valid_results
        if bool(r.get("hallucination_detected")) or r.get("verdict") == "Fail"
    ]

    if flagged:
        for idx, r in enumerate(flagged, start=1):
            story.append(Paragraph(f"Response {idx} — Row {escape(_safe(r.get('row_id', 'N/A')))}", styles["Heading3"]))
            story.append(_paragraph(f"Question: {_safe(r.get('question', ''))}", styles["BodySafe"]))
            story.append(_paragraph(f"AI Response: {_safe(r.get('ai_response', ''))}", styles["BodySafe"]))
            story.append(_paragraph(
                f"Verdict: {_safe(r.get('verdict', ''))} | Overall Score: {_safe(r.get('overall_score', ''))}/5",
                styles["BodySafe"]
            ))
            claims = r.get("flagged_claims", []) or []
            if claims:
                story.append(Paragraph("Flagged claims:", styles["BodySafe"]))
                for claim in claims:
                    if isinstance(claim, dict):
                        story.append(_paragraph(
                            f"• {_safe(claim.get('claim', ''))} | Status: {_safe(claim.get('status', ''))} | Evidence: {_safe(claim.get('evidence', ''))}",
                            styles["Small"]
                        ))
                    else:
                        story.append(_paragraph(f"• {_safe(claim)}", styles["Small"]))
            issues = r.get("major_issues", []) or []
            if issues:
                story.append(_paragraph(f"Major issues: {_safe(issues)}", styles["BodySafe"]))
            story.append(Spacer(1, 3 * mm))
    else:
        story.append(Paragraph("No hallucinated or failed responses were detected in this batch.", styles["BodySafe"]))

    story.append(PageBreak())
    story.append(Paragraph("4. Improvement Recommendations", styles["Section"]))
    for rec in _recommendations(stats, results):
        story.append(_paragraph(f"• {rec}", styles["BodySafe"]))
        story.append(Spacer(1, 1.5 * mm))

    story.append(Paragraph("5. Evaluation Result Details", styles["Section"]))
    detail_rows = [["Row", "Verdict", "Overall", "Rel.", "Acc.", "Comp.", "Hall."]]
    for r in results:
        detail_rows.append([
            _safe(r.get("row_id", "")),
            _safe(r.get("verdict", "")),
            _safe(r.get("overall_score", "")),
            _safe(r.get("relevance_score", "")),
            _safe(r.get("accuracy_score", "")),
            _safe(r.get("completeness_score", "")),
            _safe(r.get("hallucination_score", "")),
        ])
    if len(detail_rows) == 1:
        detail_rows.append(["-", "No results", "-", "-", "-", "-", "-"])
    detail = Table(detail_rows, colWidths=[18*mm, 34*mm, 20*mm, 18*mm, 18*mm, 20*mm, 18*mm], repeatRows=1)
    detail.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(detail)

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "This report is generated from the batch evaluation results produced by the AI Response Validation System.",
        styles["Small"]
    ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer.getvalue()


# Keep the existing single-report API available.
def generate_single_evaluation_pdf(result):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=17*mm)
    styles = _build_styles()
    story = [Paragraph("AI Response Validation System", styles["ReportTitle"]), Paragraph("Single Evaluation Report", styles["Title"]), Spacer(1, 5*mm)]
    story.append(_paragraph(f"Question: {_safe(result.get('question', ''))}", styles["BodySafe"]))
    story.append(_paragraph(f"AI Response: {_safe(result.get('response', ''))}", styles["BodySafe"]))
    story.append(Spacer(1, 3*mm))
    v = result.get("verdict", {}) or {}
    scores = [["Dimension", "Score"], ["Relevance", _safe(result.get("relevance", {}).get("relevance_score", ""))], ["Accuracy", _safe(result.get("accuracy", {}).get("accuracy_score", ""))], ["Completeness", _safe(result.get("completeness", {}).get("completeness_score", ""))], ["Hallucination", "1" if result.get("hallucination", {}).get("hallucination_detected") else "5"], ["Overall", _safe(v.get("overall_score", ""))]]
    t=Table(scores,colWidths=[80*mm,85*mm],repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f2937")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.4,colors.grey),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.whitesmoke])]))
    story.append(t)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"Verdict: {_safe(v.get('verdict', ''))}", styles["Section"]))
    story.append(_paragraph(f"Reasoning: {_safe(v.get('reasoning', ''))}", styles["BodySafe"]))
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer.getvalue()
