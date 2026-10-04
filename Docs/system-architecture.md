# System Architecture and Data Flow

## 1. System Overview

The AI Response Validation System is a Streamlit-based evaluation
platform that receives AI-generated responses and evaluates them across
relevance, accuracy, hallucination, and completeness.

The platform supports:

-   Single-response evaluation
-   Batch CSV evaluation
-   Structured scoring
-   Dashboard analytics
-   PDF report export

------------------------------------------------------------------------

## 2. High-Level Architecture

``` text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌───────────────────┐               ┌──────────────────┐
        │ Single Evaluation │               │ Batch CSV Upload │
        └─────────┬─────────┘               └────────┬─────────┘
                  │                                  │
                  └────────────────┬─────────────────┘
                                   ▼
                      ┌─────────────────────────┐
                      │ Evaluation Input /      │
                      │ Batch Validation        │
                      └────────────┬────────────┘
                                   ▼
                      ┌─────────────────────────┐
                      │ Reference Knowledge /   │
                      │ Retrieval Context       │
                      └────────────┬────────────┘
                                   ▼
                      ┌─────────────────────────┐
                      │ Evaluation Orchestrator │
                      └────────────┬────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      ┌─────────────┐       ┌─────────────┐      ┌───────────────┐
      │ Relevance   │       │ Accuracy    │      │ Hallucination │
      │ Judge       │       │ Judge       │      │ Detector      │
      └─────────────┘       └─────────────┘      └───────────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Completeness      │
                         │ Judge             │
                         └─────────┬─────────┘
                                   ▼
                         ┌───────────────────┐
                         │ Verdict Agent     │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
             ┌─────────────┐               ┌──────────────┐
             │ Dashboard   │               │ PDF Report   │
             └─────────────┘               └──────────────┘
```

------------------------------------------------------------------------

## 3. Major Components

### 3.1 Streamlit Application

`app.py` provides the user interface.

It supports:

-   Single evaluation input
-   Batch CSV upload
-   Evaluation controls
-   Score display
-   Reasoning display
-   Dashboard metrics
-   PDF download

### 3.2 Evaluation Input

Single evaluation accepts:

``` text
question
ai_response
reference_answer (optional)
source_context (optional)
```

Batch evaluation accepts CSV columns:

``` text
question
ai_response
reference_answer (optional)
source_context (optional)
```

### 3.3 Reference Retrieval

The retrieval layer provides source context that can be used by accuracy
and hallucination evaluation.

The current implementation uses a lightweight TF-IDF retriever based on
scikit-learn.

### 3.4 Evaluation Orchestrator

The orchestrator coordinates the four judge components and then passes
their outputs to the Verdict Agent.

Flow:

``` text
Input
 ↓
Relevance
 ↓
Accuracy
 ↓
Hallucination
 ↓
Completeness
 ↓
Verdict
```

The orchestrator returns one structured evaluation dictionary.

------------------------------------------------------------------------

## 4. Judge Agents

### Relevance Judge

Determines whether the response answers the question.

### Accuracy Judge

Checks factual correctness against reference/source information.

### Hallucination Detector

Checks response claims against source context and identifies unsupported
or contradicted claims.

### Completeness Judge

Identifies important requirements and determines whether they are
addressed, partially addressed, or missing.

------------------------------------------------------------------------

## 5. Verdict Agent

The Verdict Agent is deterministic rather than another LLM judge.

It:

1.  Converts dimension scores into numeric values.
2.  Converts hallucination detection into a 1/5 quality score.
3.  Applies the defined weights.
4.  Identifies major issues.
5.  Applies critical failure rules.
6.  Produces the final verdict.

------------------------------------------------------------------------

## 6. Batch Evaluation Architecture

``` text
CSV
 ↓
Pandas DataFrame
 ↓
Column Validation
 ↓
Record Preparation
 ↓
Batch Evaluation
 ↓
Structured Row Results
 ↓
Local Verdict Aggregation
 ↓
Statistics
 ↓
Dashboard
 ↓
PDF Report
```

Required columns:

``` text
question
ai_response
```

Optional columns:

``` text
reference_answer
source_context
```

------------------------------------------------------------------------

## 7. Dashboard Data Flow

Dashboard values are generated from the structured batch result.

``` text
Batch Results
      ↓
Statistics Calculation
      ↓
Streamlit Metrics
      ↓
Charts
      ↓
Detailed Evaluation Table
      ↓
Failed / Flagged Results
```

This prevents dashboard values from being manually entered.

------------------------------------------------------------------------

## 8. PDF Data Flow

``` text
Batch Evaluation Results
          ↓
Batch Statistics
          ↓
PDF Report Generator
          ↓
ReportLab
          ↓
PDF Bytes
          ↓
Streamlit Download
```

The report contains batch summaries, dimension scores, flagged
responses, recommendations, and result details.

------------------------------------------------------------------------

## 9. Project Structure

``` text
AI-Response-Validation-System/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
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
│   ├── input_module/
│   │   └── input_handler.py
│   ├── scoring/
│   │   └── scorer.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── pdf_report.py
│   └── llm_client.py
├── data/
├── tests/
└── app.py
```

------------------------------------------------------------------------

## 10. LLM Integration

The system uses the Google GenAI client for structured evaluation
responses.

Structured output is requested using JSON-compatible schemas so
downstream Python code receives predictable fields.

Temporary API failures can be retried using bounded retry logic.

API keys are stored in environment variables rather than source code.

------------------------------------------------------------------------

## 11. Security and Configuration

The Gemini API key is loaded through `.env`.

The `.gitignore` should exclude:

``` text
.env
__pycache__/
.pytest_cache/
```

API credentials must never be committed to GitHub.

------------------------------------------------------------------------

## 12. Error Handling

The system validates:

-   Missing question
-   Missing AI response
-   Missing required CSV columns
-   Empty batch data
-   Evaluation errors
-   PDF generation errors

The batch workflow is designed so an individual evaluation error can be
represented without unnecessarily discarding valid results.

------------------------------------------------------------------------

## 13. Current Architecture Limitations

The current implementation is a lightweight evaluation platform.

Known limitations include:

-   No persistent historical evaluation database is currently required
    by the active dashboard implementation.
-   Quality trend visualization is based on the current evaluated batch
    rather than a long-term historical database.
-   Retrieval currently uses TF-IDF rather than a dedicated production
    vector database.
-   Real LLM evaluations depend on API availability and quota.
-   Automated tests mock LLM responses to keep testing deterministic.

These limitations should be considered when presenting the project as a
prototype.
