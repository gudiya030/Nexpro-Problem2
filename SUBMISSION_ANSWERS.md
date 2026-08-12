# Submission Template — Problem 2 Answers

## Candidate details
- Full name: [YOUR FULL NAME]
- Email: [YOUR EMAIL]
- Date submitted: 12 August 2026
- Repository link: [YOUR GITHUB REPOSITORY]
- Total time spent: [ACTUAL TIME SPENT]

## Problem 2 — judge model / generator model
- Judge: Gemini, configured through `JUDGE_MODEL`
- Generator: Gemini, configured through `GENERATOR_MODEL`
- The two configurations are independent so the judge can be moved to a different model family without changing generator code.

## 2.1 Architecture Diagram / Flowchart
Use `architecture.png`.

Flow:
Test suite JSON/YAML → judging-prompt construction → judge model call → structured verdict parse/validation → malformed-JSON fallback → per-case aggregation → suite report.

For A/B evaluation, the same pair is evaluated in both A→B and B→A order before the winner is declared.

## 2.2 Setup & Run Instructions

Prerequisites:
- Python 3.10+
- Internet connection
- Gemini API key

Environment variables:
- GEMINI_API_KEY
- JUDGE_MODEL
- GENERATOR_MODEL
- JUDGE_TEMPERATURE

Install:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Run suite:
```powershell
python judge.py --suite data/test_suite.json --report reports/suite_report.json
```

A/B:
```powershell
python judge.py --suite data/test_suite.json --ab --report reports/ab_report.json
```

Bias probes:
```powershell
python judge.py --bias-probes --report reports/bias_report.json
```

Judge & generator independently configured:
Yes. `JUDGE_MODEL` and `GENERATOR_MODEL` are separate environment variables.

## 2.3 Evaluation Results

### 2.3.1 Judging mode & rubric

Judging mode: **Pointwise scoring**.

| Criterion | Definition | Weight |
|---|---|---:|
| Correctness | Factual accuracy and correctness | 30% |
| Faithfulness | Claims supported by input/reference | 20% |
| Completeness | Important answer content covered | 20% |
| Instruction-following | Format, length and audience followed | 20% |
| Tone / safety | Clear, professional and safe | 10% |

Pass rule: weighted score ≥ 3.5/5 and no criterion below 2.

### 2.3.2 Bias handling

| Bias | Mitigation | Real result |
|---|---|---|
| Position | Evaluate both A→B and B→A; calculate flip rate | [PASTE REAL OUTPUT] |
| Verbosity | Concise vs padded probe; rubric does not reward unsupported length | [PASTE REAL OUTPUT] |
| Self-enhancement | Independent judge/generator config; use different family for final study when available | [PASTE REAL OUTPUT] |
| Sycophancy/style | Confidently-wrong probe + criterion grounding | [PASTE REAL OUTPUT] |
| Score clustering | Explicit 1–5 anchors | [PASTE REAL SCORE DISTRIBUTION] |

### 2.3.3 Judge validation

| Method | Result |
|---|---|
| Human/gold agreement | [RUN AND PASTE] |
| Cohen's kappa/correlation | [RUN IF HUMAN LABELS AVAILABLE] |
| Test-retest flip rate | [RUN AND PASTE] |
| Adversarial probe | [PASTE VERDICT] |

### 2.3.4 A/B comparison

Run the A/B command and copy the generated `ab_summary`.

| Config | Pass rate | Mean score | Win rate |
|---|---:|---:|---:|
| Config A | [REAL] | [REAL] | [REAL] |
| Config B | [REAL] | [REAL] | [REAL] |

Declared winner: [USE REAL GENERATED RESULT].

## 2.4 Design Decisions & Trade-offs

### Judging mode
I chose pointwise scoring because it gives a diagnostic score for each quality dimension instead of reducing evaluation to a single preference. This makes failures easier to inspect and aggregate across the suite. Pairwise judging is still useful for direct A/B preference, so the project supports A/B comparison separately.

### Structured verdict and malformed JSON
The judge is requested to return a fixed JSON schema. The response is parsed and validated with Pydantic. If parsing or validation fails, the pipeline makes one repair request and tries again. The raw response, latency and retry count are logged for auditability.

### Judge vs generator family
The project keeps judge and generator configuration independent. In a production evaluation I would prefer a different judge family from the generator to reduce self-enhancement risk.

### Most important bias
Position bias is especially important for A/B judging because a model can change its preference when the order changes. The same pair is therefore evaluated in both orders and a flip rate is reported. Confidence in the mitigation should come from the measured result, not an assumption.

### Release gating
I would not let an LLM judge be the only release gate. I would combine it with fixed regression tests, minimum criterion thresholds, consistency checks, adversarial probes, and human review for borderline, safety-sensitive or high-impact cases.

## 2.5 Subtask Evidence & Reflection

The assignment asks for this section in the candidate's own words. After running the project, replace the placeholders below with what actually happened.

### Screenshot — auditable prompt + response
Paste a screenshot from `logs/judge_runs.jsonl`.

### Screenshot — position-bias result
Paste a screenshot of `reports/bias_report.json` or terminal output.

### Explain your position-bias check
Write in your own words how the same A/B pair was scored in both orders and what a high flip rate would mean.

### Adversarial probe outcome
Paste the actual confidently-wrong verdict and explain whether the judge was fooled.

### AI usage disclosure
State honestly which AI tools were used and which parts you personally ran, checked and edited.
