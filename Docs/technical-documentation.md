# Technical Documentation

## Development of AI Response Validation System with Hallucination Detection Assistance

**Organization:** Infosys Springboard
**Batch:** 3 (2026–27)
**Technology:** Python, Google Gemini API, Streamlit, Pydantic, Scikit-learn, Pandas, ReportLab
**Repository:** `AI-Response-Validation-System`

---

## 1. Project Overview

The **AI Response Validation System** is a multi-agent evaluation framework designed to assess the quality and reliability of AI-generated responses.

The system evaluates an AI response across four major dimensions:

* **Relevance**
* **Accuracy**
* **Completeness**
* **Hallucination**

These evaluations are combined by a **Verdict Agent**, which calculates an overall quality score and produces a final verdict:

* `Pass`
* `Needs Improvement`
* `Fail`

The system supports both **single-response evaluation** and **batch evaluation using CSV files**.

It also provides:

* Interactive Streamlit dashboard
* Evaluation statistics
* Quality trends
* Hallucination frequency
* Failed-response analysis
* PDF report generation
* Automated end-to-end testing

---

## 2. Objectives

The main objectives of the system are:

1. Automatically evaluate AI-generated responses.
2. Identify irrelevant or off-topic responses.
3. Check factual accuracy using reference answers and available source context.
4. Detect unsupported or contradicted claims.
5. Measure how completely a response answers the given question.
6. Combine individual evaluation dimensions into an overall quality score.
7. Support evaluation of multiple responses through CSV batch processing.
8. Provide visual evaluation metrics through a dashboard.
9. Generate structured PDF evaluation reports.
10. Provide a reusable framework for testing different AI systems.

---

## 3. Technology Stack

| Component            | Technology          |
| -------------------- | ------------------- |
| Programming Language | Python              |
| LLM                  | Google Gemini       |
| LLM SDK              | Google GenAI        |
| Structured Output    | Pydantic            |
| Retrieval            | Scikit-learn TF-IDF |
| Data Processing      | Pandas              |
| Frontend             | Streamlit           |
| PDF Generation       | ReportLab           |
| Testing              | Pytest              |
| Configuration        | Python-dotenv       |
| Numerical Processing | NumPy               |

---

## 4. System Architecture

The system follows a modular multi-agent architecture.

```text
                    ┌──────────────────────┐
                    │      User Input      │
                    │ Question + Response  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Input Module      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Retrieval / Source   │
                    │      Context         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
      ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐
      │  Relevance   │ │   Accuracy   │ │  Hallucination  │
      │    Judge     │ │    Judge     │ │    Detector     │
      └──────┬───────┘ └──────┬───────┘ └────────┬────────┘
             │                │                   │
             └────────────────┼───────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ Completeness Judge   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Verdict Agent     │
                    │ Score + Final Verdict│
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    ▼                      ▼
             ┌─────────────┐       ┌─────────────┐
             │  Dashboard  │       │ PDF Report  │
             └─────────────┘       └─────────────┘
```

---

# 5. Project Structure

```text
AI-Response-Validation-System/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── research.md
│   ├── evaluation-metrics.md
│   ├── system-architecture.md
│   ├── technical-documentation.md
│   └── final-project-report.md
│
├── src/
│   ├── agents/
│   │   ├── relevance_judge.py
│   │   ├── accuracy_judge.py
│   │   ├── hallucination_detector.py
│   │   ├── completeness_judge.py
│   │   ├── verdict_agent.py
│   │   └── batch_evaluation_agent.py
│   │
│   ├── evaluation/
│   │   └── batch_evaluator.py
│   │
│   ├── input_module/
│   │   └── input_handler.py
│   │
│   ├── retrieval/
│   │   └── retriever.py
│   │
│   ├── scoring/
│   │   └── scorer.py
│   │
│   ├── reporting/
│   │   └── pdf_report.py
│   │
│   ├── evaluation/
│   │   └── orchestrator.py
│   │
│   └── llm_client.py
│
├── tests/
│   ├── test_relevance.py
│   ├── test_accuracy.py
│   ├── test_hallucination.py
│   ├── test_completeness.py
│   ├── test_verdict.py
│   ├── test_batch_evaluation.py
│   └── test_m4_end_to_end.py
│
├── data/
│
└── app.py
```

---

# 6. LLM Integration

The system uses the **Google Gemini API** for structured AI-based evaluation.

The Gemini client is initialized using an API key stored in an environment variable.

```text
GEMINI_API_KEY=your_api_key
```

The API key is loaded using `python-dotenv`.

The `.env` file is excluded from Git using `.gitignore`.

### Structured Output

Each evaluation agent uses a Pydantic schema to define the expected output.

For example:

```python
class RelevanceResult(BaseModel):
    relevance_score: Literal["1", "2", "3", "4", "5"]
    reasoning: str
```

The LLM is instructed to return structured JSON matching the schema.

This makes the output predictable and easier for the application to process.

---

# 7. Input Module

The input module accepts:

### Single Evaluation

* Question
* AI-generated response
* Optional reference answer
* Optional source context

### Batch Evaluation

CSV input containing:

```text
question
ai_response
reference_answer
source_context
```

Only `question` and `ai_response` are mandatory.

The reference answer and source context are optional.

---

# 8. Retrieval Module

The retrieval component provides source context when required for evaluation.

The current implementation uses **TF-IDF-based retrieval with Scikit-learn**.

The retriever:

1. Stores documents.
2. Converts documents into TF-IDF vectors.
3. Converts the query into a TF-IDF representation.
4. Calculates similarity.
5. Returns the most relevant source content.

The current implementation does **not** use a dedicated vector database.

Similarly, documentation should not claim a production embedding/vector-database architecture unless such functionality is actually implemented.

---

# 9. Relevance Judge

The Relevance Judge determines whether the AI response addresses the user's question.

### Input

```text
Question
AI Response
```

### Output

```text
relevance_score
reasoning
```

### Scoring

| Score | Meaning               |
| ----- | --------------------- |
| 5     | Fully relevant        |
| 4     | Mostly relevant       |
| 3     | Partially relevant    |
| 2     | Mostly irrelevant     |
| 1     | Completely irrelevant |

The agent focuses specifically on relevance rather than factual correctness.

---

# 10. Accuracy Judge

The Accuracy Judge evaluates factual correctness.

It can use:

* Reference answer
* Retrieved/source context

### Output

```text
accuracy_score
reasoning
evidence
```

The evaluator considers whether the claims in the response agree with the available reference information.

The score uses the same 1–5 scale.

---

# 11. Hallucination Detection Agent

The Hallucination Detection Agent identifies claims that are not supported by the available evidence.

Each flagged claim contains:

```text
claim
status
reasoning
evidence
```

Possible statuses include:

```text
unsupported
contradicted
```

The overall output contains:

```text
hallucination_detected
flagged_claims
overall_reasoning
```

### Example

```text
Claim:
"Paris is the capital of Germany."

Status:
contradicted

Evidence:
"Paris is the capital of France."

Reasoning:
The claim conflicts with the available source information.
```

---

# 12. Completeness Judge

The Completeness Judge checks whether the response covers the important requirements of the question.

It identifies:

* Addressed aspects
* Partially addressed aspects
* Missing aspects
* Reasoning

### Output Structure

```text
completeness_score
addressed_aspects
partial_aspects
missing_aspects
reasoning
```

### Scoring

| Score | Interpretation           |
| ----- | ------------------------ |
| 5     | Fully complete           |
| 4     | Mostly complete          |
| 3     | Partially complete       |
| 2     | Substantially incomplete |
| 1     | Very incomplete          |

The agent does not penalize the response for information that is not reasonably required by the question.

---

# 13. Verdict Agent

The Verdict Agent combines the four evaluation dimensions.

### Weights

| Dimension     | Weight |
| ------------- | -----: |
| Relevance     |    25% |
| Accuracy      |    30% |
| Completeness  |    25% |
| Hallucination |    20% |

The hallucination score is converted as:

```text
No hallucination detected → 5
Hallucination detected → 1
```

### Overall Score

```text
Overall Score =
(Relevance × 0.25)
+ (Accuracy × 0.30)
+ (Completeness × 0.25)
+ (Hallucination × 0.20)
```

### Verdict Rules

```text
4.0 – 5.0  → Pass
2.5 – 3.99 → Needs Improvement
1.0 – 2.49 → Fail
```

### Critical Failure Conditions

The response receives a `Fail` verdict when:

* Accuracy score = 1
* Hallucination is detected

These conditions override the weighted overall score.

---

# 14. Evaluation Orchestrator

The `EvaluationOrchestrator` coordinates the complete single-response evaluation workflow.

```text
Input
  ↓
Relevance Judge
  ↓
Accuracy Judge
  ↓
Hallucination Detector
  ↓
Completeness Judge
  ↓
Verdict Agent
  ↓
Final Evaluation Result
```

The orchestrator returns a dictionary containing:

```text
question
response
relevance
accuracy
hallucination
completeness
verdict
```

Each agent result is converted into a serializable structure using Pydantic's `model_dump()`.

---

# 15. Batch Evaluation

The batch evaluator accepts a CSV file and processes multiple AI responses.

### Required Columns

```text
question
ai_response
```

### Optional Columns

```text
reference_answer
source_context
```

The batch workflow is:

```text
CSV Upload
   ↓
CSV Validation
   ↓
Record Preparation
   ↓
Batch AI Evaluation
   ↓
Local Verdict Calculation
   ↓
Aggregation
   ↓
Dashboard
   ↓
PDF Report
```

The system records individual evaluation results for every row.

Batch results contain fields such as:

```text
row_id
question
ai_response
relevance_score
accuracy_score
completeness_score
hallucination_score
hallucination_detected
flagged_claims
addressed_aspects
partial_aspects
missing_aspects
overall_score
verdict
major_issues
reasoning
```

---

# 16. Batch Statistics

The system calculates aggregate statistics including:

* Total responses
* Successful evaluations
* Failed evaluations
* Average relevance
* Average accuracy
* Average completeness
* Average hallucination score
* Average overall quality score
* Pass count
* Needs Improvement count
* Fail count
* Hallucination frequency

These metrics are used by the dashboard and PDF report.

---

# 17. Streamlit Dashboard

The Streamlit application provides an interactive interface for evaluating AI responses.

The dashboard displays:

### Summary Metrics

```text
Total Responses
Successful
Failed
Pass Rate
Average Quality Score
```

### Verdict Distribution

```text
Pass
Needs Improvement
Fail
```

### Dimension Metrics

```text
Average Relevance
Average Accuracy
Average Completeness
Average Hallucination
```

### Hallucination Metric

The dashboard displays the frequency of responses where hallucination was detected.

### Charts

The application provides:

* Average Dimension Scores chart
* Verdict Distribution chart
* Quality Trend chart

The current quality trend represents the evaluation results in the current batch order. Persistent historical trend analysis would require storing results across multiple runs.

---

# 18. Detailed Evaluation Results

The dashboard provides a detailed table containing individual evaluation results.

Users can inspect:

* Question
* AI response
* Individual dimension scores
* Hallucination status
* Overall score
* Verdict

A separate failed-evaluation section helps identify responses requiring further review.

---

# 19. PDF Report Generation

The system uses **ReportLab** to generate structured PDF reports.

The batch report includes:

### 1. Batch Summary

* Total responses
* Successful evaluations
* Failed evaluations
* Pass rate
* Needs Improvement count
* Fail count
* Average overall score
* Hallucination frequency

### 2. Dimension Breakdown

* Relevance
* Accuracy
* Completeness
* Hallucination

### 3. Flagged Responses

Responses containing hallucinations or failures are included with relevant details.

The report can include:

* Question
* AI response
* Verdict
* Overall score
* Flagged claims
* Evidence
* Major issues

### 4. Improvement Recommendations

Recommendations are generated based on identified weak areas such as:

* Low relevance
* Low accuracy
* Low completeness
* Hallucination detection
* Failed evaluations

### 5. Evaluation Details

A consolidated table contains:

```text
Row
Verdict
Overall Score
Relevance
Accuracy
Completeness
Hallucination
```

The generated report is available through the Streamlit download button.

---

# 20. Error Handling

The application handles several failure scenarios.

### Invalid Input

The system validates required input fields before evaluation.

### Invalid CSV

The batch evaluator checks that required columns are present.

### Missing Optional Data

If reference answers or source context are not available, the corresponding fields are treated as empty.

### LLM/API Errors

Temporary Gemini service errors can be retried.

Errors such as quota exhaustion may still require waiting or changing the API/project quota configuration.

### Batch-Level Errors

A failure in one batch record should not unnecessarily prevent other valid records from being processed.

---

# 21. Testing

The project uses **Pytest** for automated testing.

The M4 end-to-end test suite covers:

* Single evaluation workflow
* Batch evaluation workflow
* Verdict calculation
* Dashboard-related calculations
* PDF report generation
* Error-handling scenarios
* Data flow between evaluation components

The final M4 end-to-end test run produced:

```text
8 passed in 2.04s
```

This confirms that the implemented M4 test cases passed successfully in the tested environment.

---

# 22. Installation

Clone the project repository and create a virtual environment.

```bash
git clone https://github.com/Agrasha29/AI-Response-Validation-System.git
cd AI-Response-Validation-System
```

Create the environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The required packages include:

```text
google-genai
pydantic
python-dotenv
numpy
scikit-learn
pytest
streamlit
pandas
reportlab
```

---

# 23. Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

The API key should never be committed to GitHub.

The `.gitignore` should contain:

```text
.env
__pycache__/
.pytest_cache/
*.pyc
```

---

# 24. Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application provides options for:

```text
Single Evaluation
Batch Evaluation
Dashboard
PDF Report Export
```

---

# 25. Running Tests

Run the complete test suite:

```bash
python -m pytest -q
```

Run the M4 end-to-end tests:

```bash
python -m pytest -q tests/test_m4_end_to_end.py
```

Expected M4 result from the completed test run:

```text
8 passed in 2.04s
```

---

# 26. Data Flow

The complete single-response data flow is:

```text
User
 ↓
Question + AI Response
 ↓
Input Handler
 ↓
Retrieval / Source Context
 ↓
Relevance Judge
 ↓
Accuracy Judge
 ↓
Hallucination Detector
 ↓
Completeness Judge
 ↓
Verdict Agent
 ↓
Evaluation Result
 ↓
Dashboard / PDF
```

For batch processing:

```text
CSV
 ↓
Validation
 ↓
Batch Evaluation Agent
 ↓
Individual Results
 ↓
Verdict Calculation
 ↓
Statistics
 ↓
Dashboard
 ↓
PDF Report
```

---

# 27. Security and Configuration Considerations

The system uses an external LLM API, therefore API credentials must be protected.

Security practices include:

* API keys stored in `.env`
* `.env` excluded from version control
* No API keys hardcoded in Python files
* Structured model outputs used to reduce unexpected response formats
* Input validation before evaluation

Production deployment should additionally consider authentication, authorization, rate limiting, logging controls, and secure secret management.

---

# 28. Current Limitations

The current implementation has several limitations:

1. Retrieval currently uses TF-IDF rather than a dedicated vector database.
2. Evaluation quality depends on the underlying LLM.
3. Gemini API quota/rate limits can affect evaluation availability.
4. Historical dashboard trends are not persisted across application runs.
5. The current system does not yet provide a dedicated production database.
6. Final comparison of two distinct AI systems requires actual evaluation runs and collected results.
7. Benchmark evaluation results should be recorded from actual executions rather than assumed values.

---

# 29. Future Enhancements

Potential future improvements include:

* Embedding-based semantic retrieval
* Dedicated vector database
* Persistent evaluation database
* Historical dashboard analytics
* Authentication and role-based access
* More benchmark datasets
* Human-in-the-loop evaluation
* Automated regression testing
* Evaluation result versioning
* More advanced hallucination verification
* Support for additional LLM providers
* Production deployment
* Monitoring and observability

---

# 30. Conclusion

The AI Response Validation System provides a modular framework for evaluating AI-generated responses using multiple specialized evaluation agents.

The system combines:

* Relevance evaluation
* Accuracy evaluation
* Hallucination detection
* Completeness evaluation
* Weighted verdict generation
* Batch processing
* Dashboard visualization
* PDF reporting
* Automated testing


