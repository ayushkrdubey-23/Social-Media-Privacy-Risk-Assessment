"""
Flask routes for privacy assessment submission, retrieval,
recommendations, and deletion.

The API accepts self-reported questionnaire responses and returns
derived privacy-risk information.

Raw questionnaire responses are not persisted by these routes and
are not included in successful response payloads.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.services.assessment_repository import (
    delete_assessment,
    get_assessment,
    get_assessment_recommendations,
    save_assessment,
)
from backend.services.assessment_service import (
    run_assessment_from_payload,
)


assessment_bp = Blueprint(
    "assessment",
    __name__,
    url_prefix="/api/assessment",
)


def _build_public_assessment_response(
    assessment_result: dict,
    saved_record: dict,
) -> dict:
    """
    Build a privacy-safe API response.

    Raw questionnaire responses are deliberately excluded.
    """
    assessment = assessment_result["assessment"]

    return {
        "assessment_id": saved_record["assessment_id"],
        "overall_score": assessment["risk"]["overall_score"],
        "risk_level": assessment["risk"]["risk_level"],
        "risk_description": assessment["risk"]["risk_description"],
        "category_scores": assessment["risk"]["category_scores"],
        "category_details": assessment["risk"]["category_details"],
        "findings": assessment["findings"],
        "finding_summary": assessment["finding_summary"],
        "recommendations": assessment["recommendations"],
        "recommendation_summary": (
            assessment["recommendation_summary"]
        ),
        "created_at": saved_record["created_at"],
        "question_count": assessment["metadata"]["question_count"],
        "category_count": assessment["metadata"]["category_count"],
        "educational_only": assessment["metadata"]["educational_only"],
        "privacy_note": (
            "Raw questionnaire responses and direct personal "
            "identifiers are not stored by the assessment system."
        ),
    }


@assessment_bp.post("")
def create_assessment():
    """
    Create and persist a new privacy assessment.

    Expected JSON:
        {
            "responses": {
                "Q001": "PRIVATE",
                ...
                "Q050": "YES"
            }
        }
    """
    if not request.is_json:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "JSON_REQUIRED",
                    "message": (
                        "Content-Type must be "
                        "application/json."
                    ),
                },
            }
        ), 415

    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INVALID_JSON",
                    "message": "Request body contains invalid JSON.",
                },
            }
        ), 400

    result = run_assessment_from_payload(payload)

    if not result["valid"]:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Assessment responses are invalid.",
                    "details": result["validation"],
                },
            }
        ), 400

    try:
        saved_record = save_assessment(result)

    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "ASSESSMENT_PERSISTENCE_ERROR",
                    "message": str(exc),
                },
            }
        ), 400

    except Exception:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": (
                        "The assessment could not be saved."
                    ),
                },
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Assessment completed successfully.",
            "assessment": _build_public_assessment_response(
                assessment_result=result,
                saved_record=saved_record,
            ),
        }
    ), 201


@assessment_bp.get("/<assessment_id>/recommendations")
def retrieve_assessment_recommendations(
    assessment_id: str,
):
    """
    Retrieve recommendations for one saved assessment.
    """
    try:
        recommendations = get_assessment_recommendations(
            assessment_id
        )

    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ASSESSMENT_ID",
                    "message": str(exc),
                },
            }
        ), 400

    if recommendations is None:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": (
                        f"Assessment '{assessment_id}' "
                        "was not found."
                    ),
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "assessment_id": recommendations[
                "assessment_id"
            ],
            "recommendation_count": recommendations[
                "recommendation_count"
            ],
            "recommendations": recommendations[
                "recommendations"
            ],
            "privacy_note": recommendations[
                "privacy_note"
            ],
        }
    ), 200


@assessment_bp.delete("/<assessment_id>")
def remove_assessment(
    assessment_id: str,
):
    """
    Permanently delete a saved assessment and its derived records.
    """
    try:
        deleted = delete_assessment(
            assessment_id
        )

    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ASSESSMENT_ID",
                    "message": str(exc),
                },
            }
        ), 400

    if not deleted:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": (
                        f"Assessment '{assessment_id}' "
                        "was not found."
                    ),
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "message": "Assessment deleted successfully.",
            "assessment_id": str(
                assessment_id
            ).strip(),
            "privacy_note": (
                "Associated category scores and findings were "
                "deleted with the assessment."
            ),
        }
    ), 200


@assessment_bp.get("/<assessment_id>")
def retrieve_assessment(
    assessment_id: str,
):
    """
    Retrieve one persisted assessment by its generated ID.

    Only derived assessment information is returned.
    """
    try:
        assessment = get_assessment(
            assessment_id
        )

    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ASSESSMENT_ID",
                    "message": str(exc),
                },
            }
        ), 400

    if assessment is None:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": (
                        f"Assessment '{assessment_id}' "
                        "was not found."
                    ),
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "assessment": assessment,
        }
    ), 200