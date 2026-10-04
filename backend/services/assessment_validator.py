"""
Validation utilities for social media privacy assessments.

This module validates only the structured questionnaire responses.
It does not accept or store passwords, contact details, exact locations,
private messages, or other direct personal-information values.
"""

from typing import Any

from backend.services.questionnaire import get_all_questions


ALLOWED_SUBMISSION_FIELDS = {"responses"}


def normalize_response(value: Any) -> str:
    """
    Normalize a questionnaire response for consistent validation.

    Returns:
        A stripped, uppercase string.
    """
    if not isinstance(value, str):
        return ""

    return value.strip().upper()


def validate_single_response(question_id: str, response: Any) -> dict:
    """
    Validate one answer against the corresponding questionnaire item.

    Returns:
        A dictionary containing:
        - valid
        - question_id
        - response
        - errors
    """
    normalized_id = str(question_id).strip().upper()
    normalized_response = normalize_response(response)

    questions = get_all_questions()
    question_map = {question["id"]: question for question in questions}

    if normalized_id not in question_map:
        return {
            "valid": False,
            "question_id": normalized_id,
            "response": normalized_response,
            "errors": [f"Unknown question ID: {normalized_id}"],
        }

    question = question_map[normalized_id]
    allowed_options = {
        str(option).strip().upper()
        for option in question["options"]
    }

    errors = []

    if not normalized_response:
        errors.append("Response cannot be empty.")
    elif normalized_response not in allowed_options:
        errors.append(
            f"Invalid response for {normalized_id}. "
            f"Allowed responses: {sorted(allowed_options)}"
        )

    return {
        "valid": not errors,
        "question_id": normalized_id,
        "response": normalized_response,
        "errors": errors,
    }


def validate_assessment_responses(responses: Any) -> dict:
    """
    Validate the complete set of questionnaire responses.

    The expected structure is:
        {
            "Q001": "PUBLIC",
            "Q002": "FRIENDS",
            ...
            "Q050": "YES"
        }

    Returns:
        A privacy-safe validation result.
    """
    questions = get_all_questions()
    expected_question_ids = {question["id"] for question in questions}

    if not isinstance(responses, dict):
        return {
            "valid": False,
            "errors": ["Responses must be provided as a JSON object."],
            "missing_questions": sorted(expected_question_ids),
            "unknown_questions": [],
            "cleaned_responses": {},
            "answered_questions": 0,
            "total_questions": len(expected_question_ids),
        }

    submitted_question_ids = {
        str(question_id).strip().upper()
        for question_id in responses.keys()
    }

    missing_questions = sorted(
        expected_question_ids - submitted_question_ids
    )

    unknown_questions = sorted(
        submitted_question_ids - expected_question_ids
    )

    cleaned_responses = {}
    errors = []

    if missing_questions:
        errors.append(
            f"Missing required questions: {', '.join(missing_questions)}"
        )

    if unknown_questions:
        errors.append(
            f"Unknown question IDs: {', '.join(unknown_questions)}"
        )

    for question_id, response in responses.items():
        normalized_id = str(question_id).strip().upper()

        if normalized_id not in expected_question_ids:
            continue

        result = validate_single_response(normalized_id, response)

        if result["valid"]:
            cleaned_responses[normalized_id] = result["response"]
        else:
            errors.extend(result["errors"])

    return {
        "valid": not errors,
        "errors": errors,
        "missing_questions": missing_questions,
        "unknown_questions": unknown_questions,
        "cleaned_responses": cleaned_responses,
        "answered_questions": len(cleaned_responses),
        "total_questions": len(expected_question_ids),
    }


def validate_submission_payload(payload: Any) -> dict:
    """
    Validate the complete API-style assessment payload.

    Expected structure:
        {
            "responses": {
                "Q001": "PUBLIC",
                ...
                "Q050": "YES"
            }
        }

    No additional payload fields are accepted at this stage.
    This deliberately keeps the assessment privacy-first.
    """
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ["Assessment payload must be a JSON object."],
            "validation": None,
        }

    submitted_fields = set(payload.keys())
    unexpected_fields = sorted(
        submitted_fields - ALLOWED_SUBMISSION_FIELDS
    )

    missing_fields = sorted(
        ALLOWED_SUBMISSION_FIELDS - submitted_fields
    )

    errors = []

    if missing_fields:
        errors.append(
            f"Missing required payload field(s): {', '.join(missing_fields)}"
        )

    if unexpected_fields:
        errors.append(
            f"Unexpected payload field(s): {', '.join(unexpected_fields)}"
        )

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "validation": None,
        }

    validation = validate_assessment_responses(payload["responses"])

    return {
        "valid": validation["valid"],
        "errors": validation["errors"],
        "validation": validation,
    }