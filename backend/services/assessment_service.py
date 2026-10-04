"""
Complete assessment pipeline for the
Social Media Privacy Risk Assessment Framework.

Pipeline:

Questionnaire responses
        ↓
Response validation
        ↓
Privacy feature extraction
        ↓
Weighted risk scoring
        ↓
Privacy findings
        ↓
Recommendations

This service coordinates existing engines and provides one clean entry
point for future Flask API routes.

The assessment is educational and based on self-reported responses.
It does not access social media accounts or collect direct identifiers.
"""

from __future__ import annotations

from typing import Any

from backend.services.assessment_validator import (
    validate_assessment_responses,
)
from backend.services.findings_engine import (
    generate_privacy_findings,
)
from backend.services.privacy_features import (
    extract_privacy_features,
)
from backend.services.recommendations_engine import (
    generate_recommendations,
    get_recommendation_summary,
)
from backend.services.risk_engine import (
    calculate_category_scores,
    calculate_privacy_risk,
    get_risk_level_description,
)


def run_assessment(
    responses: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the complete privacy-risk assessment pipeline.

    Args:
        responses:
            Dictionary containing all questionnaire responses.

    Returns:
        A structured result.

    For invalid input, `valid` is False and the error information is
    returned without attempting risk scoring.
    """
    validation = validate_assessment_responses(
        responses
    )

    if not validation["valid"]:
        return {
            "valid": False,
            "assessment": None,
            "validation": {
                "errors": validation["errors"],
                "missing_questions": validation[
                    "missing_questions"
                ],
                "unknown_questions": validation[
                    "unknown_questions"
                ],
                "answered_questions": validation[
                    "answered_questions"
                ],
                "total_questions": validation[
                    "total_questions"
                ],
            },
        }

    cleaned_responses = validation["cleaned_responses"]

    feature_result = extract_privacy_features(
        cleaned_responses
    )

    risk_result = calculate_privacy_risk(
        cleaned_responses
    )

    category_scores = calculate_category_scores(
        feature_result["category_averages"]
    )

    findings = generate_privacy_findings(
        category_scores
    )

    recommendations = generate_recommendations(
        findings
    )

    recommendation_summary = get_recommendation_summary(
        recommendations
    )

    assessment = {
        "responses": cleaned_responses,
        "features": {
            "question_features": feature_result[
                "question_features"
            ],
            "category_averages": feature_result[
                "category_averages"
            ],
            "overall_unweighted_average": feature_result[
                "overall_unweighted_average"
            ],
        },
        "risk": {
            "overall_score": risk_result[
                "overall_score"
            ],
            "risk_level": risk_result[
                "risk_level"
            ],
            "risk_description": get_risk_level_description(
                risk_result["risk_level"]
            ),
            "category_scores": category_scores,
            "category_details": risk_result[
                "category_details"
            ],
        },
        "findings": findings,
        "finding_summary": {
            "total": len(findings),
            "severity_counts": {
                "CRITICAL": sum(
                    1
                    for finding in findings
                    if finding["severity"] == "CRITICAL"
                ),
                "HIGH": sum(
                    1
                    for finding in findings
                    if finding["severity"] == "HIGH"
                ),
                "MEDIUM": sum(
                    1
                    for finding in findings
                    if finding["severity"] == "MEDIUM"
                ),
                "LOW": sum(
                    1
                    for finding in findings
                    if finding["severity"] == "LOW"
                ),
            },
        },
        "recommendations": recommendations,
        "recommendation_summary": recommendation_summary,
        "metadata": {
            "question_count": len(cleaned_responses),
            "category_count": len(category_scores),
            "educational_only": True,
            "data_source": "self-reported questionnaire",
        },
    }

    return {
        "valid": True,
        "assessment": assessment,
        "validation": {
            "errors": [],
            "missing_questions": [],
            "unknown_questions": [],
            "answered_questions": validation[
                "answered_questions"
            ],
            "total_questions": validation[
                "total_questions"
            ],
        },
    }


def run_assessment_from_payload(
    payload: Any,
) -> dict[str, Any]:
    """
    Run the assessment from an API-style payload.

    Expected:
        {
            "responses": {
                "Q001": "PRIVATE",
                ...
                "Q050": "YES"
            }
        }
    """
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "assessment": None,
            "validation": {
                "errors": [
                    "Assessment payload must be a JSON object."
                ],
                "missing_questions": [],
                "unknown_questions": [],
                "answered_questions": 0,
                "total_questions": 0,
            },
        }

    unexpected_fields = set(payload) - {"responses"}

    if unexpected_fields:
        return {
            "valid": False,
            "assessment": None,
            "validation": {
                "errors": [
                    "Unexpected payload field(s): "
                    + ", ".join(sorted(unexpected_fields))
                ],
                "missing_questions": [],
                "unknown_questions": [],
                "answered_questions": 0,
                "total_questions": 0,
            },
        }

    if "responses" not in payload:
        return {
            "valid": False,
            "assessment": None,
            "validation": {
                "errors": [
                    "Missing required payload field: responses"
                ],
                "missing_questions": [],
                "unknown_questions": [],
                "answered_questions": 0,
                "total_questions": 0,
            },
        }

    return run_assessment(
        payload["responses"]
    )


def get_assessment_summary(
    assessment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a compact summary suitable for API responses,
    dashboards, or report headers.
    """
    if not assessment_result.get("valid"):
        return {
            "valid": False,
            "error_count": len(
                assessment_result.get(
                    "validation",
                    {},
                ).get("errors", [])
            ),
        }

    assessment = assessment_result["assessment"]

    return {
        "valid": True,
        "overall_score": assessment["risk"][
            "overall_score"
        ],
        "risk_level": assessment["risk"][
            "risk_level"
        ],
        "risk_description": assessment["risk"][
            "risk_description"
        ],
        "finding_count": assessment[
            "finding_summary"
        ]["total"],
        "recommendation_count": assessment[
            "recommendation_summary"
        ]["total_recommendations"],
        "question_count": assessment[
            "metadata"
        ]["question_count"],
        "category_count": assessment[
            "metadata"
        ]["category_count"],
        "educational_only": assessment[
            "metadata"
        ]["educational_only"],
    }


def main() -> None:
    """
    Run a basic end-to-end pipeline check using the project's
    synthetic safe-response configuration.
    """
    from backend.services.synthetic_data import (
        SAFE_RESPONSES,
    )

    result = run_assessment(
        SAFE_RESPONSES
    )

    summary = get_assessment_summary(
        result
    )

    print("=" * 70)
    print("COMPLETE PRIVACY ASSESSMENT PIPELINE")
    print("=" * 70)
    print(f"Valid: {summary['valid']}")

    if summary["valid"]:
        print(
            "Overall score:",
            summary["overall_score"],
        )
        print(
            "Risk level:",
            summary["risk_level"],
        )
        print(
            "Findings:",
            summary["finding_count"],
        )
        print(
            "Recommendations:",
            summary["recommendation_count"],
        )
        print(
            "Questions:",
            summary["question_count"],
        )
        print(
            "Categories:",
            summary["category_count"],
        )
        print(
            "Educational only:",
            summary["educational_only"],
        )
    else:
        print(
            "Errors:",
            result["validation"]["errors"],
        )

    print("=" * 70)


if __name__ == "__main__":
    main()