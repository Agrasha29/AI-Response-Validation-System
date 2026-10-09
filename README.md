# 🤖 AI Response Validation System with Hallucination Detection Assistance

An AI-powered evaluation platform that assesses Large Language Model (LLM) responses across **relevance, factual accuracy, completeness, and potential hallucinations**. It combines structured AI evaluation, rule-based scoring, CSV batch processing, an interactive dashboard, and PDF report generation.

> **Project:** Development of AI Response Validation System with Hallucination Detection Assistance  
> **Program:** Infosys Springboard Internship — Batch 3 (2026–27)  
> **Status:** Implemented prototype — ongoing improvements

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Evaluation Dimensions](#-evaluation-dimensions)
- [Scoring and Verdict Logic](#-scoring-and-verdict-logic)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration and Security](#-configuration-and-security)
- [Using the Application](#-using-the-application)
- [Batch CSV Format](#-batch-csv-format)
- [Dashboard and PDF Reports](#-dashboard-and-pdf-reports)
- [Testing](#-testing)
- [Limitations](#-limitations)
- [Future Scope](#-future-scope)
- [References](#-references)

---

## 🔎 Overview

Generative AI systems can produce fluent and convincing answers that may still be inaccurate, incomplete, irrelevant, or unsupported by available evidence. Reviewing these answers manually can be time-consuming, especially when testing many responses.

The **AI Response Validation System** provides a structured way to inspect generated answers. A user supplies a question and an AI-generated response, with an optional reference answer or source context. The system evaluates the response across multiple dimensions, calculates a final verdict, and presents the results through a Streamlit application.

The application supports **single-response evaluation** and **CSV-based batch evaluation**. Results can be explored in a dashboard and exported as PDF reports.

### 🎯 Project Goal

To assist users in identifying response-quality issues and reviewing potentially unsupported claims through structured, explainable evaluation results.

---

## ❗ Problem Statement

AI-generated content can contain several kinds of quality problems:

- **Factual inaccuracies:** Statements that conflict with reliable information.
- **Potential hallucinations:** Claims that are unsupported by, or contradicted by, the evidence supplied for evaluation.
- **Irrelevance:** Responses that do not properly answer the question.
- **Incompleteness:** Responses that omit important requirements or parts of a question.
- **Difficult-to-review output:** Raw model responses do not always provide consistent scores or a clear summary of issues.

This project addresses these problems with a multi-dimensional evaluation workflow, explicit scoring rules, batch analysis, and report generation.

---

## 🎯 Objectives

- Evaluate AI-generated responses for relevance, accuracy, and completeness.
- Flag claims that appear unsupported or contradicted by supplied source context.
- Use optional reference answers and source context to support evidence-aware evaluation.
- Combine dimension scores using a defined weighted scoring model.
- Evaluate multiple question-response pairs from a CSV file.
- Summarize evaluation outcomes in an interactive dashboard.
- Generate downloadable PDF reports for review and documentation.
- Test the main evaluation workflows and scoring behavior.

---

## ✨ Key Features

### 🧪 Single Response Evaluation
Enter a question and AI response, and optionally provide a reference answer or source context. The system returns structured evaluation results across the supported dimensions.

### 🧩 Four Evaluation Dimensions
- **Relevance:** Does the response address the question?
- **Accuracy:** How well does the response agree with available reference information?
- **Hallucination detection:** Are claims unsupported by or contradicted by supplied evidence?
- **Completeness:** Does the response address the important aspects of the question?

### ⚖️ Weighted Verdict Engine
A local Python scoring component combines the dimension scores, applies verdict thresholds, and enforces critical failure rules.

### 📂 Batch Evaluation
Upload a CSV file to evaluate multiple question-response pairs and review row-level results and aggregate statistics.

### 📊 Evaluation Dashboard
View response counts, verdict distribution, average quality scores, dimension-level metrics, and hallucination-related statistics for the available evaluation results.

### 📄 PDF Report Generation
Export structured reports containing scores, verdicts, reasoning, and flagged issues. Report contents depend on the selected single or batch reporting workflow.

### 🧱 Structured Model Outputs
Pydantic schemas define expected evaluation fields so model results can be validated and consumed consistently.

### 🧪 Automated Tests
Pytest is used to check important evaluation and reporting workflows.

---

## 🔄 How It Works

```text
                 ┌──────────────────────────────┐
                 │         User Input           │
                 │ Question + AI Response       │
                 │ Optional Reference / Context │
                 └──────────────┬───────────────┘
                                ▼
                 ┌──────────────────────────────┐
                 │    Evaluation Orchestrator   │
                 └──────────────┬───────────────┘
                                ▼
                 ┌──────────────────────────────┐
                 │       Evaluation Layer       │
                 │ Relevance                    │
                 │ Accuracy                     │
                 │ Hallucination Detection      │
                 │ Completeness                 │
                 └──────────────┬───────────────┘
                                ▼
                 ┌──────────────────────────────┐
                 │   Local Verdict and Scoring  │
                 │ Weighted Score + Rules       │
                 └──────────────┬───────────────┘
                                │
                  ┌─────────────┴──────────────┐
                  ▼                            ▼
       ┌────────────────────┐       ┌────────────────────┐
       │ Dashboard / Results│       │ PDF Report Export  │
       └────────────────────┘       └────────────────────┘
```

### Workflow Summary

1. **Input:** The user enters a question and response or uploads a CSV file.
2. **Context:** Optional reference answers and source context support the evaluation.
3. **Evaluation:** Components assess relevance, accuracy, hallucination indicators, and completeness.
4. **Scoring:** Python logic calculates the weighted score and applies verdict rules.
5. **Presentation:** The application displays individual results and aggregate metrics.
6. **Export:** The user can download available results as a PDF report.

> **Retrieval note:** The current retrieval implementation uses TF-IDF similarity through scikit-learn. This README does not claim that an embedding-based vector database pipeline is implemented.

---

## 📏 Evaluation Dimensions

| Dimension | What it checks | Typical output |
|---|---|---|
| **Relevance** | Whether the response addresses the question | Score from 1 to 5 and reasoning |
| **Accuracy** | Whether the response agrees with the supplied reference answer or source context | Score from 1 to 5, reasoning, and evidence where available |
| **Hallucination Detection** | Whether claims appear unsupported or contradicted by supplied source context | Detection flag, flagged claims, status, reasoning, and evidence |
| **Completeness** | Whether important requirements are addressed | Score from 1 to 5, addressed aspects, partial aspects, and missing aspects |

### Score Interpretation

| Score | General interpretation |
|---:|---|
| 5 | Excellent / fully satisfied |
| 4 | Mostly satisfied, with minor issues |
| 3 | Partially satisfied |
| 2 | Significant issues |
| 1 | Very poor / largely unsatisfied |

The exact interpretation depends on the dimension being evaluated.

---

## ⚖️ Scoring and Verdict Logic

The current verdict engine uses these weights:

| Dimension | Weight |
|---|---:|
| Relevance | 25% |
| Accuracy | 30% |
| Completeness | 25% |
| Hallucination score | 20% |
| **Total** | **100%** |

The weighted score is:

\[
S = 0.25R + 0.30A + 0.25C + 0.20H
\]

Where `R` is relevance, `A` is accuracy, `C` is completeness, and `H` is the hallucination score. In the current verdict logic, the hallucination score is **5 when no hallucination is detected** and **1 when a hallucination is detected**.

### Verdict Thresholds

| Weighted score | Verdict |
|---|---|
| 4.00–5.00 | **Pass** |
| 2.50–3.99 | **Needs Improvement** |
| 1.00–2.49 | **Fail** |

### Critical Failure Rules

The current implementation assigns **Fail** when:
- The accuracy score is `1`, or
- A hallucination is detected.

These rules can override the weighted score. The verdict is an automated assessment, not a guarantee that a response is factually correct or incorrect.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application logic and orchestration |
| **Google Gemini API** | LLM-powered evaluation |
| **Streamlit** | Interactive web application and dashboard |
| **Pydantic** | Structured response schemas and validation |
| **Pandas** | CSV handling and batch-result aggregation |
| **scikit-learn** | TF-IDF-based text retrieval |
| **ReportLab** | PDF report generation |
| **Pytest** | Automated testing |
| **Git & GitHub** | Version control and project hosting |

---

## 📁 Project Structure

```text
AI-Response-Validation-System/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── docs/
│   ├── research.md
│   ├── evaluation-metrics.md
│   ├── system-architecture.md
│   └── ...project documentation
├── src/
│   ├── agents/
│   │   ├── relevance_judge.py
│   │   ├── accuracy_judge.py
│   │   ├── hallucination_detector.py
│   │   ├── completeness_judge.py
│   │   ├── verdict_agent.py
│   │   └── batch_evaluation_agent.py
│   ├── evaluation/
│   │   ├── orchestrator.py
│   │   └── batch_evaluator.py
│   ├── retrieval/
│   │   └── retriever.py
│   ├── reporting/
│   │   └── pdf_report.py
│   └── llm_client.py
├── tests/
│   └── ...automated tests
└── data/
    └── ...optional reference and test data
```

> File names may differ slightly between revisions. Keep this tree synchronized with the actual repository if modules are renamed or moved.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies.
- A Google Gemini API key.
- Git (optional, for cloning the repository).

### 1. Clone the Repository

```bash
git clone https://github.com/Agrasha29/AI-Response-Validation-System.git
cd AI-Response-Validation-System
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the requirements file does not contain every dependency used by your checkout, install the missing packages and update `requirements.txt`. The project commonly uses:

```bash
pip install google-genai pydantic python-dotenv pandas numpy scikit-learn streamlit reportlab pytest
```

### 4. Configure the API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own key. Do not commit the real `.env` file to GitHub.

### 5. Run the Application

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

---

## 🔐 Configuration and Security

The LLM client reads the API key from the `GEMINI_API_KEY` environment variable.

Recommended `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example
venv/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
```

You may create `.env.example` with a placeholder only:

```env
GEMINI_API_KEY=replace_with_your_key
```

**Never** place a working API key in source code, screenshots, documentation, test data, or commits. If a real key has been committed or exposed, revoke or rotate it.

---

## 🖥️ Using the Application

### Single Evaluation

1. Open **Single Evaluation**.
2. Enter the question and AI-generated response.
3. Optionally provide a reference answer or source context.
4. Start the evaluation.
5. Review dimension scores, reasoning, flagged claims, and the final verdict.
6. Download the available single-evaluation PDF report.

### Batch Evaluation

1. Open **Batch Evaluation**.
2. Upload a CSV file with the required columns.
3. Validate the file and start batch evaluation.
4. Review row-level results and summary statistics.
5. Inspect the dashboard and download the batch PDF report.

### Dashboard

The dashboard summarizes the evaluation results available to the application. Depending on the current workflow and session state, it can display:

- Number of responses evaluated
- Successful and failed evaluation counts
- Verdict counts and pass rate
- Average quality and dimension scores
- Hallucination frequency
- Batch-level quality trend
- Detailed evaluation results

Historical trends across application restarts require persistent storage. Session-only results should not be described as permanent history.

---

## 📄 Batch CSV Format

Required columns:
- `question`
- `ai_response`

Optional columns:
- `reference_answer`
- `source_context`

### Example

```csv
question,ai_response,reference_answer,source_context
"What is Python?","Python is a high-level programming language.","Python is a high-level, interpreted programming language.","Python is a high-level, interpreted programming language known for its readability."
"What is the capital of France?","The capital of France is Berlin.","Paris is the capital of France.","Paris is the capital of France."
```

Save the file as UTF-8 CSV. Use quotation marks around values containing commas or line breaks. The example is illustrative input data, not a claim about actual evaluation scores.

---

## 📊 Dashboard and PDF Reports

### Dashboard Metrics

The dashboard summarizes row-level evaluations to make results easier to interpret. When validating a build, compare aggregate metrics against the detailed result table.

### PDF Reports

The reporting module uses ReportLab to create downloadable reports for supported evaluation workflows. Depending on the report type and current implementation, reports can include:

- Evaluation summary
- Question and AI response
- Dimension-level scores
- Overall score and verdict
- Evaluation reasoning
- Flagged claims and supporting details
- Missing aspects and improvement suggestions

A PDF reflects the data returned by the evaluation pipeline; it does not independently verify the factual accuracy of the model's judgments.

---

## 🧪 Testing

Run the project's tests from the repository root:

```bash
python -m pytest -q
```

To run the M4 end-to-end test file, if it exists in your checkout:

```bash
python -m pytest -q tests/test_m4_end_to_end.py
```

A previously completed run of that test file reported:

```text
8 passed in 2.04s
```

This result applies to that specific test run and file. Run the tests again after changes to confirm the current repository state.

Recommended test areas include:
- Correct and incorrect responses
- Incomplete and irrelevant answers
- Supported, unsupported, and contradicted claims
- Verdict thresholds and critical failure rules
- CSV validation and batch aggregation
- Dashboard calculations
- PDF generation
- Missing configuration and API quota errors

---

## ⚠️ Limitations

- Evaluation results depend on the language model, prompt design, input quality, and available evidence.
- Hallucination detection is evidence-dependent and may produce false positives or false negatives.
- Without a reference answer or source context, factual verification may be less reliable.
- TF-IDF retrieval is based on text similarity and is not equivalent to embedding-based semantic retrieval.
- Gemini API requests are subject to model- and project-specific quotas and rate limits.
- Large batch requests may be constrained by request limits, token limits, or response-size constraints.
- Dashboard trends are limited to the data retained by the current implementation; durable cross-session history requires persistent storage.
- The system assists review and quality assurance; it does not replace expert judgment in high-stakes settings.

---

## 🔮 Future Scope

- Add persistent storage for evaluations and historical dashboards.
- Build side-by-side model comparison into the interface.
- Improve retrieval with embeddings and a vector store where justified.
- Add claim-level evidence matching and evaluation confidence indicators.
- Improve rate-limit-aware batching, retries, and progress reporting.
- Support configurable scoring weights and domain-specific evaluation criteria.
- Compare automated judgments against human-labeled benchmark data.
- Expand automated tests and add evaluation-quality metrics.
- Introduce authentication and access control for multi-user deployments.

---

## 📚 References

- **Gemini API Documentation:** https://ai.google.dev/gemini-api/docs
- **Gemini API Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits
- **Streamlit Documentation:** https://docs.streamlit.io/
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **scikit-learn Documentation:** https://scikit-learn.org/stable/
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **ReportLab Documentation:** https://docs.reportlab.com/
- **Pytest Documentation:** https://docs.pytest.org/
- **RAGAS:** https://docs.ragas.io/
- **TruLens:** https://www.trulens.org/
- **TruthfulQA:** https://github.com/sylinrl/TruthfulQA
- **SQuAD:** https://rajpurkar.github.io/SQuAD-explorer/

RAGAS, TruLens, TruthfulQA, and SQuAD are included as related frameworks or reference resources; this README does not imply that all of them are integrated into the current application.

---

## 👩‍💻 Project Context

**Project:** Development of AI Response Validation System with Hallucination Detection Assistance  
**Program:** Infosys Springboard Internship — Batch 3 (2026–27)

This repository documents the implementation and ongoing development of a system for structured evaluation of AI-generated responses, potential hallucination detection, batch analysis, dashboard visualization, and report generation.

---

<p align="center">
  <b>Built to make AI response evaluation more structured, transparent, and easier to review. 🤖</b>
</p>
