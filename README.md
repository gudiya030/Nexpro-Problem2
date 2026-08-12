# Nexpro — Problem 2: LLM-as-Judge Evaluation Pipeline

This is the complete runnable implementation for **Problem 2** of the supplied Nexpro Applied AI / ML Engineering assignment.

## What is implemented

1. Fixed **20-case JSON test suite**.
2. Structured judging prompt.
3. Pointwise 1–5 rubric:
   - Correctness 30%
   - Faithfulness 20%
   - Completeness 20%
   - Instruction-following 20%
   - Tone/safety 10%
4. Structured JSON verdict with Pydantic validation.
5. Malformed JSON recovery: parse → extract JSON → retry once.
6. Per-case aggregation and pass rate.
7. A/B comparison.
8. Position-bias check using the same pair in both orders.
9. Verbosity probe.
10. Confidently-wrong / sycophancy probe.
11. Independent `JUDGE_MODEL` and `GENERATOR_MODEL` configuration.
12. Auditable JSONL logs containing prompt, raw response, latency and retry count.
13. Mock mode for checking the pipeline without an API key.

## Setup

Python 3.10+.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Gemini API key.

### Run the real 20-case suite

```powershell
python judge.py --suite data/test_suite.json --report reports/suite_report.json
```

### Run A/B evaluation

```powershell
python judge.py --suite data/test_suite.json --ab --report reports/ab_report.json
```

### Run bias probes

```powershell
python judge.py --bias-probes --report reports/bias_report.json
```

### Local smoke test

```powershell
python judge.py --suite data/test_suite.json --mock --report reports/mock_report.json
python judge.py --suite data/test_suite.json --mock --ab --report reports/mock_ab_report.json
python judge.py --bias-probes --mock --report reports/mock_bias_report.json
```

Mock results are only for checking code flow. They are not final submission evidence.

## Files

- `judge.py` — evaluation pipeline
- `generator.py` — independent generator utility
- `data/test_suite.json` — 20 fixed evaluation cases
- `architecture.png` — architecture diagram
- `.env.example` — configuration template
- `requirements.txt` — dependencies
- `README.md` — setup and explanation
- `reports/` — generated reports
- `logs/` — audit logs

## Evidence required before submission

After the real run, take screenshots of:

1. One raw prompt + raw judge response from `logs/judge_runs.jsonl`.
2. The position-bias report from `reports/bias_report.json`.
3. The adversarial confidently-wrong verdict.
4. The terminal showing the real command and generated metrics.

Do not use mock numbers in the final submission.
