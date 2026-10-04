# Evaluation Metrics and Scoring Methodology

## 1. Overview

The AI Response Validation System evaluates every response using four
dimensions:

1.  Relevance
2.  Accuracy
3.  Completeness
4.  Hallucination Detection

Each dimension is normalized to a **1--5 scale** before the final
verdict is calculated.

------------------------------------------------------------------------

## 2. Relevance Score

    Score Interpretation
  ------- ---------------------------------------------------
        5 Directly and fully addresses the question
        4 Mostly relevant with minor unnecessary content
        3 Partially relevant
        2 Mostly off-topic or misses important requirements
        1 Does not meaningfully answer the question

The Relevance Judge returns:

``` text
relevance_score
reasoning
```

------------------------------------------------------------------------

## 3. Accuracy Score

    Score Interpretation
  ------- ------------------------------------------
        5 Factually correct and well supported
        4 Mostly correct with minor issues
        3 Partially correct
        2 Contains significant factual errors
        1 Fundamentally incorrect or contradictory

The Accuracy Judge uses a reference answer and/or source context when
available.

It returns:

``` text
accuracy_score
evidence
reasoning
```

------------------------------------------------------------------------

## 4. Hallucination Score

Hallucination is represented as a quality dimension:

``` text
5 = No hallucination detected
1 = Hallucination detected
```

The detector separately returns:

``` text
hallucination_detected
flagged_claims
overall_reasoning
```

Each flagged claim contains:

``` text
claim
status
reasoning
evidence
```

Possible statuses:

-   `unsupported`
-   `contradicted`

A hallucination is treated as a **critical failure** by the Verdict
Agent.

------------------------------------------------------------------------

## 5. Completeness Score

    Score Interpretation
  ------- --------------------------------------------------------
        5 Fully complete
        4 Mostly complete with minor omissions
        3 Partially complete with meaningful missing information
        2 Substantially incomplete
        1 Very incomplete

The Completeness Judge also identifies:

``` text
addressed_aspects
partial_aspects
missing_aspects
reasoning
```

------------------------------------------------------------------------

## 6. Weighted Overall Score

The project uses the following weights:

  Dimension         Weight
  --------------- --------
  Relevance            25%
  Accuracy             30%
  Completeness         25%
  Hallucination        20%

Formula:

``` text
Overall Score =
(Relevance × 0.25)
+ (Accuracy × 0.30)
+ (Completeness × 0.25)
+ (Hallucination × 0.20)
```

The result is rounded to two decimal places.

------------------------------------------------------------------------

## 7. Verdict Thresholds

    Overall Score Verdict
  --------------- -------------------
       4.00--5.00 Pass
       2.50--3.99 Needs Improvement
       1.00--2.49 Fail

### Critical Failure Rules

Two conditions override the normal weighted threshold:

``` text
Accuracy score = 1
OR
Hallucination detected = True
```

Either condition produces:

``` text
Fail
```

This ensures that a high average score cannot hide a critical factual
failure or detected hallucination.

------------------------------------------------------------------------

## 8. Example

Suppose:

``` text
Relevance     = 5
Accuracy      = 4
Completeness  = 4
Hallucination = 5
```

Then:

``` text
(5 × 0.25)
+ (4 × 0.30)
+ (4 × 0.25)
+ (5 × 0.20)

= 1.25 + 1.20 + 1.00 + 1.00
= 4.45
```

Final verdict:

``` text
Pass
```

If the hallucination detector instead identifies a hallucinated claim,
the final verdict becomes:

``` text
Fail
```

because hallucination is a critical failure.

------------------------------------------------------------------------

## 9. Batch Metrics

For a batch, the dashboard calculates:

-   Total responses
-   Successful evaluations
-   Failed evaluations
-   Pass count
-   Needs Improvement count
-   Fail count
-   Pass/Needs Improvement/Fail percentages
-   Average relevance
-   Average accuracy
-   Average completeness
-   Average hallucination score
-   Average overall score
-   Hallucination count
-   Hallucination rate
-   Current-batch quality trend

A metric is calculated from the structured evaluation records produced
by the batch evaluator.

------------------------------------------------------------------------

## 10. Metric Interpretation

The scores should be interpreted together.

For example:

``` text
High relevance + low accuracy
```

means the response addresses the question but contains factual problems.

``` text
High accuracy + low completeness
```

means the information provided is correct but important aspects are
missing.

``` text
High weighted score + hallucination detected
```

still produces `Fail` because hallucination is treated as a critical
failure.

------------------------------------------------------------------------

## 11. Consistency Validation

Repeated evaluation of similar question-answer pairs should be used to
inspect:

-   Score stability
-   Reasoning stability
-   Hallucination decisions
-   Verdict stability

Automated tests validate deterministic application logic, while
real-model consistency should be evaluated separately using
representative repeated inputs.
