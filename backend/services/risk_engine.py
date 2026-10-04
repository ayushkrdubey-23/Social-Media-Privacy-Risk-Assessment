"""
Weighted privacy risk scoring engine.

This module converts extracted privacy features into:
- 10 category risk scores,
- one weighted overall score from 0 to 100,
- one educational risk classification.

Higher scores indicate greater privacy exposure.

This is an educational risk-assessment model based on self-reported
responses and configured assumptions. It is not a professional security
guarantee, certification, or prediction of real-world harm.
"""

from __future__ import annotations

from typing import Any

from backend.services.privacy_features import (
    extract_privacy_features,
)
from backend.utils.constants import (
    RISK_CATEGORIES,
    RISK_LEVELS,
)


MIN_SCORE = 0.0
MAX_SCORE = 100.0


def _clamp_score(score: float) -> float:
    """
    Keep a score inside the project's 0-100 range.
    """
    return round(
        max(
            MIN_SCORE,
            min(MAX_SCORE, float(score)),
        ),
        2,
    )


def validate_scoring_configuration() -> dict[str, Any]:
    """
    Validate category weights and risk-level configuration.

    Returns:
        A configuration validation summary.
    """
    errors: list[str] = []

    if not RISK_CATEGORIES:
        errors.append("No risk categories are configured.")

    total_weight = sum(
        float(category["weight"])
        for category in RISK_CATEGORIES.values()
    )

    if round(total_weight, 2) != 100:
        errors.append(
            f"Category weights must total 100. "
            f"Current total: {total_weight}"
        )

    expected_levels = {
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL",
    }

    actual_levels = set(RISK_LEVELS)

    if actual_levels != expected_levels:
        errors.append(
            "Risk levels must contain exactly LOW, MODERATE, "
            "HIGH, and CRITICAL."
        )

    for level_name, level_config in RISK_LEVELS.items():
        minimum = float(level_config["min"])
        maximum = float(level_config["max"])

        if minimum < MIN_SCORE:
            errors.append(
                f"{level_name} minimum is below {MIN_SCORE}."
            )

        if maximum > MAX_SCORE:
            errors.append(
                f"{level_name} maximum is above {MAX_SCORE}."
            )

        if minimum > maximum:
            errors.append(
                f"{level_name} minimum exceeds maximum."
            )

    return {
        "valid": not errors,
        "errors": errors,
        "category_count": len(RISK_CATEGORIES),
        "weight_total": round(total_weight, 2),
        "risk_level_count": len(RISK_LEVELS),
    }


def classify_risk_level(score: float) -> str:
    """
    Classify a 0-100 score according to configured thresholds.
    """
    normalized_score = _clamp_score(score)

    for level_name, level_config in RISK_LEVELS.items():
        minimum = float(level_config["min"])
        maximum = float(level_config["max"])

        if minimum <= normalized_score <= maximum:
            return level_name

    raise ValueError(
        f"Unable to classify risk score: {normalized_score}"
    )


def calculate_category_scores(
    category_averages: dict[str, float],
) -> dict[str, float]:
    """
    Normalize the extracted category averages into final category
    risk scores.
    """
    configured_categories = set(RISK_CATEGORIES)
    supplied_categories = set(category_averages)

    missing_categories = sorted(
        configured_categories - supplied_categories
    )

    unknown_categories = sorted(
        supplied_categories - configured_categories
    )

    if missing_categories:
        raise ValueError(
            "Missing category scores: "
            + ", ".join(missing_categories)
        )

    if unknown_categories:
        raise ValueError(
            "Unknown categories: "
            + ", ".join(unknown_categories)
        )

    return {
        category: _clamp_score(category_averages[category])
        for category in RISK_CATEGORIES
    }


def calculate_weighted_overall_score(
    category_scores: dict[str, float],
) -> float:
    """
    Calculate the weighted overall risk score.

    Category scores are 0-100 and configured weights total 100.
    """
    validated_scores = calculate_category_scores(category_scores)

    weighted_score = 0.0

    for category, config in RISK_CATEGORIES.items():
        score = validated_scores[category]
        weight = float(config["weight"])

        weighted_score += score * (weight / 100.0)

    return _clamp_score(weighted_score)


def calculate_privacy_risk(
    responses: dict[str, Any],
) -> dict[str, Any]:
    """
    Run feature extraction and weighted privacy-risk calculation.

    Args:
        responses:
            Complete questionnaire response dictionary.

    Returns:
        Complete explainable risk-assessment result.
    """
    configuration = validate_scoring_configuration()

    if not configuration["valid"]:
        raise ValueError(
            "Risk scoring configuration is invalid: "
            + "; ".join(configuration["errors"])
        )

    feature_result = extract_privacy_features(responses)

    category_scores = calculate_category_scores(
        feature_result["category_averages"]
    )

    overall_score = calculate_weighted_overall_score(
        category_scores
    )

    risk_level = classify_risk_level(overall_score)

    category_details = {}

    for category, config in RISK_CATEGORIES.items():
        category_score = category_scores[category]
        weight = float(config["weight"])

        category_details[category] = {
            "score": category_score,
            "weight": weight,
            "weighted_contribution": round(
                category_score * weight / 100.0,
                2,
            ),
            "description": config["description"],
        }

    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "category_scores": category_scores,
        "category_details": category_details,
        "feature_summary": {
            "question_count": len(
                feature_result["question_features"]
            ),
            "category_count": len(
                feature_result["category_averages"]
            ),
            "unweighted_average": feature_result[
                "overall_unweighted_average"
            ],
        },
        "scoring_model": {
            "score_minimum": MIN_SCORE,
            "score_maximum": MAX_SCORE,
            "category_weight_total": configuration["weight_total"],
            "risk_levels": RISK_LEVELS,
            "educational_only": True,
        },
    }


def get_risk_level_description(risk_level: str) -> str:
    """
    Return the configured educational description for a risk level.
    """
    normalized_level = str(risk_level).strip().upper()

    if normalized_level not in RISK_LEVELS:
        raise ValueError(
            f"Unknown risk level: {normalized_level}"
        )

    return str(
        RISK_LEVELS[normalized_level]["description"]
    )


def get_risk_score_summary(
    risk_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a compact summary suitable for APIs and dashboards.
    """
    risk_level = str(risk_result["risk_level"])

    return {
        "overall_score": risk_result["overall_score"],
        "risk_level": risk_level,
        "risk_description": get_risk_level_description(
            risk_level
        ),
        "category_scores": risk_result["category_scores"],
        "category_weights": {
            category: float(config["weight"])
            for category, config in RISK_CATEGORIES.items()
        },
    }


def main() -> None:
    """
    Verify the scoring configuration.
    """
    result = validate_scoring_configuration()

    print("=" * 70)
    print("PRIVACY RISK SCORING CONFIGURATION")
    print("=" * 70)
    print(f"Valid: {result['valid']}")
    print(f"Categories: {result['category_count']}")
    print(f"Weight total: {result['weight_total']}")
    print(f"Risk levels: {result['risk_level_count']}")

    if result["errors"]:
        print("\nConfiguration errors:")

        for error in result["errors"]:
            print(f"- {error}")
    else:
        print("Scoring configuration is valid.")

    print("=" * 70)


if __name__ == "__main__":
    main()