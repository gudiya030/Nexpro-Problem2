import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

CRITERIA = {
    "correctness": 0.30,
    "faithfulness": 0.20,
    "completeness": 0.20,
    "instruction_following": 0.20,
    "tone_safety": 0.10,
}


def build_prompt(case, answer, label):
    return f"""
You are an independent LLM evaluator.

Evaluate the candidate answer objectively.

Criteria:
1. correctness - factual accuracy
2. faithfulness - supported by the provided information
3. completeness - covers important requirements
4. instruction_following - follows the user's instructions
5. tone_safety - clear, professional and safe

Score every criterion from 1 to 5.

USER INPUT:
{case.get("input", "")}

REFERENCE / EXPECTED OUTPUT:
{case.get("expected_output", "")}

CANDIDATE LABEL:
{label}

CANDIDATE ANSWER:
{answer}

Return ONLY valid JSON with this structure:

{{
  "correctness": {{
    "score": 1,
    "rationale": "..."
  }},
  "faithfulness": {{
    "score": 1,
    "rationale": "..."
  }},
  "completeness": {{
    "score": 1,
    "rationale": "..."
  }},
  "instruction_following": {{
    "score": 1,
    "rationale": "..."
  }},
  "tone_safety": {{
    "score": 1,
    "rationale": "..."
  }},
  "overall_score": 1,
  "pass_fail": "FAIL",
  "overall_rationale": "..."
}}

Score from 1 to 5 only.

PASS when:
- overall_score >= 3.5
- no criterion has a score below 2
"""


def validate(data, case_id):
    for name in CRITERIA:
        if name not in data:
            raise ValueError(
                f"Missing criterion: {name}"
            )

        if "score" not in data[name]:
            raise ValueError(
                f"Missing score: {name}"
            )

        score = int(data[name]["score"])

        if score < 1 or score > 5:
            raise ValueError(
                f"Invalid score: {name}"
            )

    if "overall_score" not in data:
        raise ValueError(
            "Missing overall_score"
        )

    if "pass_fail" not in data:
        raise ValueError(
            "Missing pass_fail"
        )

    return {
        "case_id": case_id,

        "criteria": {
            name: {
                "score": int(
                    data[name]["score"]
                ),
                "rationale": data[name].get(
                    "rationale",
                    ""
                )
            }
            for name in CRITERIA
        },

        "overall_score": float(
            data["overall_score"]
        ),

        "pass_fail": str(
            data["pass_fail"]
        ).upper(),

        "overall_rationale": data.get(
            "overall_rationale",
            ""
        )
    }


def mock_judge(case):
    criteria = {}

    for name in CRITERIA:
        criteria[name] = {
            "score": 4,
            "rationale": "Mock evaluation."
        }

    return {
        "case_id": case["id"],
        "criteria": criteria,
        "overall_score": 4.0,
        "pass_fail": "PASS",
        "overall_rationale": "Mock evaluation."
    }


def real_judge(
    client,
    model,
    case,
    answer,
    label
):
    prompt = build_prompt(
        case,
        answer,
        label
    )

    schema = {
        "type": "object",

        "properties": {
            "correctness": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "rationale": {
                        "type": "string"
                    }
                },
                "required": [
                    "score",
                    "rationale"
                ]
            },

            "faithfulness": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "rationale": {
                        "type": "string"
                    }
                },
                "required": [
                    "score",
                    "rationale"
                ]
            },

            "completeness": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "rationale": {
                        "type": "string"
                    }
                },
                "required": [
                    "score",
                    "rationale"
                ]
            },

            "instruction_following": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "rationale": {
                        "type": "string"
                    }
                },
                "required": [
                    "score",
                    "rationale"
                ]
            },

            "tone_safety": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "rationale": {
                        "type": "string"
                    }
                },
                "required": [
                    "score",
                    "rationale"
                ]
            },

            "overall_score": {
                "type": "number",
                "minimum": 1,
                "maximum": 5
            },

            "pass_fail": {
                "type": "string"
            },

            "overall_rationale": {
                "type": "string"
            }
        },

        "required": [
            "correctness",
            "faithfulness",
            "completeness",
            "instruction_following",
            "tone_safety",
            "overall_score",
            "pass_fail",
            "overall_rationale"
        ]
    }

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=schema
        )
    )

    data = json.loads(
        response.text
    )

    return validate(
        data,
        case["id"]
    )


def run_suite(
    path,
    report_path,
    mock=False
):
    suite = json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )

    # Current Gemini model alias.
    model = os.getenv(
        "JUDGE_MODEL",
        "gemini-flash-latest"
    )

    client = None

    if not mock:
        key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing in .env"
            )

        client = genai.Client(
            api_key=key
        )

    results = []

    for case in suite["cases"]:

        answer = case.get(
            "model_output_a",
            case.get(
                "answer",
                ""
            )
        )

        if mock:
            verdict = mock_judge(
                case
            )
        else:
            verdict = real_judge(
                client,
                model,
                case,
                answer,
                "A"
            )

        results.append(
            verdict
        )

    scores = [
        r["overall_score"]
        for r in results
    ]

    passed = [
        r["pass_fail"] == "PASS"
        for r in results
    ]

    summary = {
        "cases": len(results),

        "pass_rate": round(
            sum(passed)
            / len(passed)
            * 100,
            2
        ) if results else 0,

        "mean_score": round(
            sum(scores)
            / len(scores),
            3
        ) if scores else 0
    }

    report = {
        "suite": suite.get(
            "suite_name",
            "Nexpro Problem 2"
        ),

        "mode": (
            "mock"
            if mock
            else "real"
        ),

        "judge_model": model,

        "criteria": CRITERIA,

        "results": results,

        "summary": summary
    }

    Path(
        report_path
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        report_path
    ).write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(
        json.dumps(
            summary,
            indent=2
        )
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--suite"
    )

    parser.add_argument(
        "--report",
        default="reports/report.json"
    )

    parser.add_argument(
        "--mock",
        action="store_true"
    )

    args = parser.parse_args()

    if not args.suite:
        parser.error(
            "Use --suite PATH"
        )

    run_suite(
        args.suite,
        args.report,
        args.mock
    )


if __name__ == "__main__":
    main()