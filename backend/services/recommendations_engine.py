"""
Privacy recommendations generation engine.

This module converts explainable privacy findings into practical,
user-friendly recommendations.

The recommendations are educational. They do not guarantee prevention
of privacy incidents or security compromise.

This module does NOT:
- access social media accounts,
- scrape social media,
- inspect private profiles,
- track real people,
- collect direct personal identifiers.
"""

from __future__ import annotations

from typing import Any


PRIORITY_ORDER = {
    "IMMEDIATE": 3,
    "IMPORTANT": 2,
    "GOOD PRACTICE": 1,
}


RECOMMENDATION_MAP: dict[str, dict[str, Any]] = {
    "PROFILE_VISIBILITY_EXPOSURE": {
        "recommendation": (
            "Restrict profile visibility to the smallest audience that "
            "matches your needs and review profile discovery settings."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Review profile visibility, profile-photo visibility, and "
            "account discovery settings."
        ),
    },
    "PERSONAL_INFORMATION_EXPOSURE": {
        "recommendation": (
            "Restrict sensitive profile-information categories and remove "
            "unnecessary public exposure."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Review date-of-birth, phone-number, email, and other sensitive "
            "profile-field visibility."
        ),
    },
    "LOCATION_PRIVACY_EXPOSURE": {
        "recommendation": (
            "Disable unnecessary location sharing and limit the audience "
            "for location-related content."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Review application location permissions, location tags, and "
            "real-time location sharing."
        ),
    },
    "CONTENT_PRIVACY_EXPOSURE": {
        "recommendation": (
            "Review the audience of posts and older content before keeping "
            "information publicly visible."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Audit older public posts, review post audiences, and consider "
            "privacy before sharing photos or videos."
        ),
    },
    "CONNECTION_PRIVACY_EXPOSURE": {
        "recommendation": (
            "Review connection requests and restrict connection-list "
            "visibility where possible."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Audit followers and connections periodically and avoid "
            "accepting suspicious or impersonating accounts."
        ),
    },
    "TAGGING_MENTION_EXPOSURE": {
        "recommendation": (
            "Enable tag review and restrict who can tag or mention your "
            "account."
        ),
        "priority": "GOOD PRACTICE",
        "action": (
            "Review tagging and mention controls and remove unwanted tags."
        ),
    },
    "ACCOUNT_SECURITY_WEAKNESS": {
        "recommendation": (
            "Strengthen account protection with a unique strong password, "
            "multi-factor authentication, session review, and maintained "
            "recovery options."
        ),
        "priority": "IMMEDIATE",
        "action": (
            "Enable multi-factor authentication, review active sessions, "
            "and verify recovery settings."
        ),
    },
    "THIRD_PARTY_ACCESS_EXPOSURE": {
        "recommendation": (
            "Remove unnecessary third-party access and review application "
            "permissions before granting access."
        ),
        "priority": "IMPORTANT",
        "action": (
            "Audit connected applications and revoke unused or unnecessary "
            "permissions."
        ),
    },
    "SOCIAL_ENGINEERING_EXPOSURE": {
        "recommendation": (
            "Treat unexpected links and unusual requests cautiously and "
            "verify identities through an independent trusted channel."
        ),
        "priority": "IMMEDIATE",
        "action": (
            "Never share passwords or verification codes and independently "
            "verify unusual requests."
        ),
    },
    "DIGITAL_FOOTPRINT_EXPOSURE": {
        "recommendation": (
            "Review your public digital footprint and reduce unnecessary "
            "exposure from old content and unused accounts."
        ),
        "priority": "GOOD PRACTICE",
        "action": (
            "Review public information, unused accounts, and repeated "
            "public identifiers."
        ),
    },
}


def validate_recommendation_configuration() -> dict[str, Any]:
    """
    Validate that every finding type has a recommendation definition.
    """
    errors: list[str] = []

    for finding_type, definition in RECOMMENDATION_MAP.items():
        if not definition.get("recommendation"):
            errors.append(
                f"Missing recommendation text for {finding_type}."
            )

        if not definition.get("action"):
            errors.append(
                f"Missing action text for {finding_type}."
            )

        priority = definition.get("priority")

        if priority not in PRIORITY_ORDER:
            errors.append(
                f"Invalid priority '{priority}' for {finding_type}."
            )

    return {
        "valid": not errors,
        "finding_type_count": len(RECOMMENDATION_MAP),
        "priority_count": len(PRIORITY_ORDER),
        "priorities": list(PRIORITY_ORDER.keys()),
        "errors": errors,
    }


def get_recommendation_for_finding(
    finding: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate one recommendation for one finding.
    """
    if not isinstance(finding, dict):
        raise ValueError("Finding must be provided as a dictionary.")

    finding_type = str(
        finding.get("finding_type", "")
    ).strip().upper()

    if not finding_type:
        raise ValueError(
            "Finding is missing a finding_type."
        )

    if finding_type not in RECOMMENDATION_MAP:
        raise ValueError(
            f"No recommendation is configured for finding type: "
            f"{finding_type}"
        )

    definition = RECOMMENDATION_MAP[finding_type]

    priority = definition["priority"]

    return {
        "finding_type": finding_type,
        "category": finding.get("category"),
        "severity": finding.get("severity"),
        "score": finding.get("score"),
        "priority": priority,
        "recommendation": definition["recommendation"],
        "action": definition["action"],
        "educational_only": True,
    }


def generate_recommendations(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Generate recommendations from a list of findings.

    Duplicate finding types are combined into one recommendation.
    Recommendations are sorted by priority and then by finding score.
    """
    if not isinstance(findings, list):
        raise ValueError("Findings must be provided as a list.")

    configuration = validate_recommendation_configuration()

    if not configuration["valid"]:
        raise ValueError(
            "Recommendation configuration is invalid: "
            + "; ".join(configuration["errors"])
        )

    recommendation_by_type: dict[str, dict[str, Any]] = {}

    for finding in findings:
        recommendation = get_recommendation_for_finding(finding)

        finding_type = recommendation["finding_type"]

        if finding_type not in recommendation_by_type:
            recommendation_by_type[finding_type] = recommendation
            continue

        current = recommendation_by_type[finding_type]

        current_score = float(current.get("score") or 0)
        new_score = float(recommendation.get("score") or 0)

        if new_score > current_score:
            recommendation_by_type[finding_type] = recommendation

    recommendations = list(
        recommendation_by_type.values()
    )

    recommendations.sort(
        key=lambda item: (
            PRIORITY_ORDER[item["priority"]],
            float(item.get("score") or 0),
        ),
        reverse=True,
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        recommendation["recommendation_id"] = (
            f"REC-{index:03d}"
        )

    return recommendations


def generate_recommendations_from_category_scores(
    category_scores: dict[str, float],
) -> dict[str, Any]:
    """
    Convenience function that generates findings and recommendations
    from category scores.

    This is useful for later API/report integration.
    """
    from backend.services.findings_engine import (
        generate_privacy_findings,
    )

    findings = generate_privacy_findings(
        category_scores
    )

    recommendations = generate_recommendations(
        findings
    )

    return {
        "finding_count": len(findings),
        "recommendation_count": len(recommendations),
        "findings": findings,
        "recommendations": recommendations,
    }


def get_recommendation_summary(
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Return priority statistics for the dashboard/report layer.
    """
    priority_counts = {
        "IMMEDIATE": 0,
        "IMPORTANT": 0,
        "GOOD PRACTICE": 0,
    }

    for recommendation in recommendations:
        priority = recommendation.get("priority")

        if priority in priority_counts:
            priority_counts[priority] += 1

    return {
        "total_recommendations": len(recommendations),
        "priority_counts": priority_counts,
    }


def main() -> None:
    """
    Verify recommendation configuration.
    """
    result = validate_recommendation_configuration()

    print("=" * 70)
    print("PRIVACY RECOMMENDATIONS CONFIGURATION")
    print("=" * 70)
    print(f"Valid: {result['valid']}")
    print(
        "Finding types:",
        result["finding_type_count"],
    )
    print(
        "Priorities:",
        result["priorities"],
    )

    if result["errors"]:
        print("\nConfiguration errors:")

        for error in result["errors"]:
            print(f"- {error}")
    else:
        print("All finding types have valid recommendations.")

    print("=" * 70)


if __name__ == "__main__":
    main()