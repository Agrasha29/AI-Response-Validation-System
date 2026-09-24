## Milestone 3 — Overall Evaluation & Verdict

### Weighted Scoring Model

The overall evaluation score is calculated using four evaluation dimensions:

| Dimension | Weight |
|---|---:|
| Relevance | 25% |
| Accuracy | 30% |
| Completeness | 25% |
| Hallucination Detection | 20% |

The overall score is calculated as:

Overall Score =
(Relevance × 0.25) +
(Accuracy × 0.30) +
(Completeness × 0.25) +
(Hallucination × 0.20)

All individual scores are normalized to a 1–5 scale before calculating the weighted score.

### Hallucination Score

The current implementation converts the hallucination detection result into a normalized score:

| Hallucination Status | Score |
|---|---:|
| No hallucination detected | 5 |
| Hallucination detected | 1 |

This provides a consistent numerical value for the weighted evaluation.

### Final Verdict Rules

The overall score is mapped to one of three verdict categories:

| Overall Score | Verdict |
|---|---|
| 4.0 – 5.0 | Pass |
| 2.5 – 3.99 | Needs Improvement |
| 1.0 – 2.49 | Fail |

### Critical Failure Rules

The score-based verdict is supplemented with critical-failure conditions.

A response is marked as **Fail** when:

- The accuracy score is critically low (`1/5`), or
- Hallucination is detected.

This prevents a high score in other dimensions from masking a critical factual or hallucination issue.

### Verdict Reasoning

The Verdict Agent also generates a consolidated reasoning summary containing:

- Individual dimension scores
- Overall weighted score
- Major issues
- Final verdict
- Summary of the response's strengths and weaknesses

### Example

Suppose an evaluation produces:

- Relevance = 5/5
- Accuracy = 4/5
- Completeness = 3/5
- Hallucination = 5/5

The weighted score is:

5 × 0.25 + 4 × 0.30 + 3 × 0.25 + 5 × 0.20 = 4.20/5

Since 4.20 falls within the 4.0–5.0 range, the score-based verdict is **Pass**.
