"""
Privacy feature extraction engine.

This module converts validated questionnaire responses into normalized
0-100 privacy exposure features.

A higher feature value means greater privacy exposure/risk.

This module does NOT:
- access social media accounts,
- scrape social media,
- inspect private profiles,
- collect real personal information,
- calculate the final weighted assessment score.

Final risk scoring is implemented separately.
"""

from __future__ import annotations

from typing import Any

from backend.services.questionnaire import get_all_questions


MIN_FEATURE_SCORE = 0
MAX_FEATURE_SCORE = 100


# ---------------------------------------------------------------------
# Explicit response -> exposure mappings
# ---------------------------------------------------------------------
#
# Each question has its own semantics.
#
# 0   = safest response
# 25  = low exposure
# 50  = moderate exposure / uncertainty
# 75  = high exposure
# 100 = highest exposure
#
# "NOT SURE" generally receives a moderate-high value because uncertainty
# itself represents a privacy-awareness gap.
# ---------------------------------------------------------------------

QUESTION_RISK_MAP: dict[str, dict[str, int]] = {
    # ---------------------------------------------------------
    # 1. Profile Visibility
    # ---------------------------------------------------------
    "Q001": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q002": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q003": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q004": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q005": {
        "YES": 0,
        "NO": 80,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 2. Personal Information
    # ---------------------------------------------------------
    "Q006": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q007": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q008": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q009": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 50,
        "NOT SURE": 65,
    },
    "Q010": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 3. Location Privacy
    # ---------------------------------------------------------
    "Q011": {
        "DISABLED": 0,
        "ENABLED": 85,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q012": {
        "YES": 0,
        "NO": 85,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q013": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q014": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 95,
        "NOT SURE": 60,
    },
    "Q015": {
        "YES": 0,
        "NO": 85,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },

    # ---------------------------------------------------------
    # 4. Posts and Content
    # ---------------------------------------------------------
    "Q016": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 100,
        "NOT SURE": 60,
    },
    "Q017": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q018": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 50,
        "NOT SURE": 65,
    },
    "Q019": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q020": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 5. Friends and Followers
    # ---------------------------------------------------------
    "Q021": {
        "NO": 0,
        "YES": 85,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },
    "Q022": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q023": {
        "YES": 0,
        "NO": 65,
        "SOMETIMES": 35,
        "NOT SURE": 60,
    },
    "Q024": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 90,
        "NOT SURE": 60,
    },
    "Q025": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 50,
        "NOT SURE": 65,
    },

    # ---------------------------------------------------------
    # 6. Tagging and Mentions
    # ---------------------------------------------------------
    "Q026": {
        "ENABLED": 0,
        "DISABLED": 80,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q027": {
        "ENABLED": 0,
        "DISABLED": 85,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },
    "Q028": {
        "NO": 0,
        "YES": 80,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },
    "Q029": {
        "YES": 0,
        "NO": 65,
        "SOMETIMES": 35,
        "NOT SURE": 60,
    },
    "Q030": {
        "YES": 0,
        "NO": 65,
        "SOMETIMES": 35,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 7. Account Security
    # ---------------------------------------------------------
    "Q031": {
        "YES": 0,
        "NO": 100,
        "SOMETIMES": 50,
        "NOT SURE": 70,
    },
    "Q032": {
        "ENABLED": 0,
        "DISABLED": 100,
        "SOMETIMES": 50,
        "NOT SURE": 70,
    },
    "Q033": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q034": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q035": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },

    # ---------------------------------------------------------
    # 8. Third-Party Applications
    # ---------------------------------------------------------
    "Q036": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q037": {
        "YES": 0,
        "NO": 80,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },
    "Q038": {
        "YES": 0,
        "NO": 80,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },
    "Q039": {
        "YES": 0,
        "NO": 85,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q040": {
        "YES": 0,
        "NO": 80,
        "SOMETIMES": 45,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 9. Messaging and Social Engineering
    # ---------------------------------------------------------
    "Q041": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q042": {
        "YES": 0,
        "NO": 90,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q043": {
        "YES": 0,
        "NO": 100,
        "SOMETIMES": 50,
        "NOT SURE": 70,
    },
    "Q044": {
        "YES": 0,
        "NO": 80,
        "SOMETIMES": 45,
        "NOT SURE": 65,
    },
    "Q045": {
        "PRIVATE": 0,
        "FRIENDS": 35,
        "PUBLIC": 90,
        "NOT SURE": 60,
    },

    # ---------------------------------------------------------
    # 10. Digital Footprint
    # ---------------------------------------------------------
    "Q046": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q047": {
        "YES": 0,
        "NO": 65,
        "SOMETIMES": 35,
        "NOT SURE": 60,
    },
    "Q048": {
        "YES": 0,
        "NO": 70,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q049": {
        "YES": 0,
        "NO": 75,
        "SOMETIMES": 40,
        "NOT SURE": 60,
    },
    "Q050": {
        "YES": 0,
        "NO": 75,
        "PARTIALLY": 40,
        "NOT SURE": 60,
    },
}


def normalize_response(response: Any) -> str:
    """
    Normalize one response value.
    """
    if not isinstance(response, str):
        return ""

    return response.strip().upper()


def validate_feature_configuration() -> dict:
    """
    Verify that every questionnaire question has a complete risk map.

    Returns:
        Validation summary.
    """
    questions = get_all_questions()
    question_ids = {question["id"] for question in questions}
    mapped_ids = set(QUESTION_RISK_MAP)

    missing_mappings = sorted(question_ids - mapped_ids)
    unknown_mappings = sorted(mapped_ids - question_ids)

    invalid_values = []

    for question in questions:
        question_id = question["id"]

        allowed_options = {
            str(option).strip().upper()
            for option in question["options"]
        }

        mapped_options = set(
            QUESTION_RISK_MAP.get(question_id, {})
        )

        missing_options = allowed_options - mapped_options
        unknown_options = mapped_options - allowed_options

        if missing_options:
            invalid_values.append(
                {
                    "question_id": question_id,
                    "type": "missing_options",
                    "values": sorted(missing_options),
                }
            )

        if unknown_options:
            invalid_values.append(
                {
                    "question_id": question_id,
                    "type": "unknown_options",
                    "values": sorted(unknown_options),
                }
            )

    return {
        "valid": (
            not missing_mappings
            and not unknown_mappings
            and not invalid_values
        ),
        "question_count": len(questions),
        "mapping_count": len(QUESTION_RISK_MAP),
        "missing_mappings": missing_mappings,
        "unknown_mappings": unknown_mappings,
        "invalid_values": invalid_values,
    }


def extract_question_feature(
    question_id: str,
    response: Any,
) -> float:
    """
    Convert one questionnaire response into a 0-100 exposure feature.

    Raises:
        ValueError: If the question or response is invalid.
    """
    normalized_id = str(question_id).strip().upper()
    normalized_response = normalize_response(response)

    if normalized_id not in QUESTION_RISK_MAP:
        raise ValueError(
            f"Unknown question ID: {normalized_id}"
        )

    if not normalized_response:
        raise ValueError(
            f"Empty response for question: {normalized_id}"
        )

    risk_mapping = QUESTION_RISK_MAP[normalized_id]

    if normalized_response not in risk_mapping:
        allowed = sorted(risk_mapping)

        raise ValueError(
            f"Invalid response '{normalized_response}' for "
            f"{normalized_id}. Allowed responses: {allowed}"
        )

    score = risk_mapping[normalized_response]

    return float(
        max(
            MIN_FEATURE_SCORE,
            min(MAX_FEATURE_SCORE, score),
        )
    )


def extract_privacy_features(
    responses: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert complete questionnaire responses into structured
    privacy features.

    Args:
        responses:
            Dictionary such as:
            {
                "Q001": "PRIVATE",
                "Q002": "FRIENDS",
                ...
                "Q050": "YES"
            }

    Returns:
        Privacy feature structure containing per-question features
        grouped by category.
    """
    configuration = validate_feature_configuration()

    if not configuration["valid"]:
        raise ValueError(
            "Feature configuration is invalid: "
            f"{configuration}"
        )

    if not isinstance(responses, dict):
        raise ValueError("Responses must be provided as a dictionary.")

    questions = get_all_questions()

    expected_ids = {question["id"] for question in questions}
    submitted_ids = {
        str(question_id).strip().upper()
        for question_id in responses
    }

    missing_questions = sorted(expected_ids - submitted_ids)
    unknown_questions = sorted(submitted_ids - expected_ids)

    if missing_questions:
        raise ValueError(
            "Missing questionnaire responses: "
            + ", ".join(missing_questions)
        )

    if unknown_questions:
        raise ValueError(
            "Unknown questionnaire responses: "
            + ", ".join(unknown_questions)
        )

    question_features: dict[str, float] = {}
    category_features: dict[str, list[float]] = {}

    question_metadata = {}

    for question in questions:
        question_id = question["id"]
        category = question["category"]

        feature_value = extract_question_feature(
            question_id=question_id,
            response=responses[question_id],
        )

        question_features[question_id] = feature_value

        category_features.setdefault(category, []).append(
            feature_value
        )

        question_metadata[question_id] = {
            "category": category,
            "feature_key": question["feature_key"],
            "response": normalize_response(responses[question_id]),
            "exposure_score": feature_value,
        }

    category_averages = {
        category: round(
            sum(values) / len(values),
            2,
        )
        for category, values in category_features.items()
    }

    overall_unweighted_average = round(
        sum(question_features.values())
        / len(question_features),
        2,
    )

    return {
        "question_features": question_features,
        "category_features": category_features,
        "category_averages": category_averages,
        "overall_unweighted_average": overall_unweighted_average,
        "question_metadata": question_metadata,
    }


def extract_privacy_features_from_validated(
    cleaned_responses: dict[str, str],
) -> dict[str, Any]:
    """
    Convenience wrapper for already validated responses.

    This function is intended for later API integration.
    """
    return extract_privacy_features(cleaned_responses)


def get_feature_summary(
    feature_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a compact summary of extracted privacy features.
    """
    return {
        "question_count": len(feature_result["question_features"]),
        "category_count": len(feature_result["category_averages"]),
        "category_averages": feature_result["category_averages"],
        "overall_unweighted_average": (
            feature_result["overall_unweighted_average"]
        ),
    }


def main() -> None:
    """
    Run a basic configuration check.
    """
    result = validate_feature_configuration()

    print("=" * 70)
    print("PRIVACY FEATURE EXTRACTION CONFIGURATION")
    print("=" * 70)
    print(f"Valid: {result['valid']}")
    print(f"Questions: {result['question_count']}")
    print(f"Risk mappings: {result['mapping_count']}")

    if result["missing_mappings"]:
        print(
            "Missing mappings:",
            result["missing_mappings"],
        )

    if result["unknown_mappings"]:
        print(
            "Unknown mappings:",
            result["unknown_mappings"],
        )

    if result["invalid_values"]:
        print(
            "Invalid mapping definitions:",
            result["invalid_values"],
        )

    if result["valid"]:
        print("All questionnaire responses have valid feature mappings.")

    print("=" * 70)


if __name__ == "__main__":
    main()
    