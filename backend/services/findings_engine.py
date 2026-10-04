"""
Privacy findings generation engine.

This module transforms privacy-risk scores into explainable findings.

The findings are educational and based only on questionnaire responses
and normalized privacy-risk features.

The module does NOT:
- inspect social media accounts,
- scrape public profiles,
- access private accounts,
- track real people,
- collect direct personal identifiers,
- claim that a finding guarantees real-world harm.
"""

from __future__ import annotations

from typing import Any

from backend.services.privacy_features import (
    extract_privacy_features,
)
from backend.services.risk_engine import (
    calculate_category_scores,
)
from backend.utils.constants import (
    RISK_CATEGORIES,
)


# ---------------------------------------------------------------------
# Category-specific finding definitions
# ---------------------------------------------------------------------
#
# Each category has explanatory templates.
# The actual category score determines severity and whether a finding
# is generated.
# ---------------------------------------------------------------------

FINDING_DEFINITIONS: dict[str, dict[str, Any]] = {
    "profile": {
        "finding_type": "PROFILE_VISIBILITY_EXPOSURE",
        "title": "Profile visibility may expose more information than intended.",
        "description": (
            "Your profile visibility settings indicate that some profile "
            "information may be accessible to a broader audience than your "
            "preferred privacy posture."
        ),
        "impact": (
            "Broader profile visibility can make publicly shared profile "
            "information easier for unknown viewers to discover and connect."
        ),
        "mitigation": (
            "Review profile visibility, discovery, and profile-photo "
            "audience settings."
        ),
    },
    "personal_information": {
        "finding_type": "PERSONAL_INFORMATION_EXPOSURE",
        "title": "Personal-information visibility needs attention.",
        "description": (
            "Your responses indicate that some categories of personal "
            "profile information may have broader visibility than intended."
        ),
        "impact": (
            "Exposed personal-information categories can increase the amount "
            "of context available to unknown viewers."
        ),
        "mitigation": (
            "Restrict sensitive profile fields and periodically review "
            "their audience settings."
        ),
    },
    "location": {
        "finding_type": "LOCATION_PRIVACY_EXPOSURE",
        "title": "Location privacy controls may need improvement.",
        "description": (
            "Your location-related responses indicate possible exposure "
            "through location sharing, tags, permissions, or posting habits."
        ),
        "impact": (
            "Repeated or unnecessary location exposure may reveal patterns "
            "about activities or routines."
        ),
        "mitigation": (
            "Review location permissions, disable unnecessary location "
            "sharing, and limit the audience for location-related content."
        ),
    },
    "content": {
        "finding_type": "CONTENT_PRIVACY_EXPOSURE",
        "title": "Published content may reveal unnecessary information.",
        "description": (
            "Your content-related responses suggest that some posts, "
            "media, or older content may have broader exposure than desired."
        ),
        "impact": (
            "Public or broadly shared content can reveal information that "
            "becomes part of your long-term digital footprint."
        ),
        "mitigation": (
            "Review post audiences, older public content, and media before "
            "sharing."
        ),
    },
    "connections": {
        "finding_type": "CONNECTION_PRIVACY_EXPOSURE",
        "title": "Connections and follower visibility may be too broad.",
        "description": (
            "Your responses indicate potential exposure through connection "
            "requests, follower visibility, or insufficient review of "
            "accounts you connect with."
        ),
        "impact": (
            "Broader connection visibility can reveal social relationships "
            "and increase exposure to unwanted or suspicious accounts."
        ),
        "mitigation": (
            "Review connection requests, periodically audit connections, "
            "and restrict connection-list visibility."
        ),
    },
    "tagging": {
        "finding_type": "TAGGING_MENTION_EXPOSURE",
        "title": "Tagging and mention controls may increase exposure.",
        "description": (
            "Your responses indicate that tags or mentions may be created "
            "or displayed without enough review or control."
        ),
        "impact": (
            "Other users can add content or references connected to your "
            "profile, potentially increasing unwanted exposure."
        ),
        "mitigation": (
            "Enable tag review where available and restrict who can tag "
            "or mention your account."
        ),
    },
    "account_security": {
        "finding_type": "ACCOUNT_SECURITY_WEAKNESS",
        "title": "Account-security practices require attention.",
        "description": (
            "Your account-security responses indicate weaknesses in areas "
            "such as strong passwords, multi-factor authentication, "
            "session review, or recovery settings."
        ),
        "impact": (
            "Weak account-security controls can increase the likelihood "
            "of unauthorized account access or account misuse."
        ),
        "mitigation": (
            "Use a unique strong password, enable multi-factor "
            "authentication, review active sessions, and maintain recovery "
            "options."
        ),
    },
    "third_party_apps": {
        "finding_type": "THIRD_PARTY_ACCESS_EXPOSURE",
        "title": "Third-party application access may be broader than needed.",
        "description": (
            "Your responses indicate that connected applications or their "
            "permissions may not be reviewed frequently enough."
        ),
        "impact": (
            "Unnecessary third-party permissions can increase the amount of "
            "account functionality or information available to external "
            "services."
        ),
        "mitigation": (
            "Review connected applications, remove unused access, and "
            "check requested permissions before granting access."
        ),
    },
    "social_engineering": {
        "finding_type": "SOCIAL_ENGINEERING_EXPOSURE",
        "title": "Social-engineering resistance could be improved.",
        "description": (
            "Your responses indicate opportunities to improve how you "
            "handle unexpected links, unusual requests, identity checks, "
            "and account messages."
        ),
        "impact": (
            "Social-engineering attacks often rely on convincing users to "
            "reveal information, open unsafe links, or trust impersonators."
        ),
        "mitigation": (
            "Verify unusual requests independently, avoid unexpected links, "
            "and never share passwords or verification codes."
        ),
    },
    "digital_footprint": {
        "finding_type": "DIGITAL_FOOTPRINT_EXPOSURE",
        "title": "Your public digital footprint may need a review.",
        "description": (
            "Your responses indicate that older accounts, public "
            "identifiers, or previously published information may deserve "
            "additional privacy review."
        ),
        "impact": (
            "Information published over time can remain discoverable through "
            "multiple online contexts and may reveal more than intended."
        ),
        "mitigation": (
            "Review public content, unused accounts, and repeated public "
            "identifiers periodically."
        ),
    },
}


# ---------------------------------------------------------------------
# Severity rules
# ---------------------------------------------------------------------

SEVERITY_THRESHOLDS = (
    (71, "CRITICAL"),
    (41, "HIGH"),
    (21, "MEDIUM"),
    (0, "LOW"),
)


def determine_severity(score: float) -> str:
    """
    Convert a category score into finding severity.

    Note:
        Severity describes the educational priority of the finding.
        It does not claim a confirmed security incident.
    """
    normalized_score = float(score)

    for minimum, severity in SEVERITY_THRESHOLDS:
        if normalized_score >= minimum:
            return severity

    return "LOW"


def validate_finding_configuration() -> dict[str, Any]:
    """
    Ensure every configured risk category has a finding definition.
    """
    configured_categories = set(RISK_CATEGORIES)
    defined_categories = set(FINDING_DEFINITIONS)

    missing_categories = sorted(
        configured_categories - defined_categories
    )

    unknown_categories = sorted(
        defined_categories - configured_categories
    )

    return {
        "valid": (
            not missing_categories
            and not unknown_categories
        ),
        "category_count": len(configured_categories),
        "finding_definition_count": len(defined_categories),
        "missing_categories": missing_categories,
        "unknown_categories": unknown_categories,
    }


def generate_category_finding(
    category: str,
    score: float,
) -> dict[str, Any]:
    """
    Generate one explainable finding for a category.
    """
    normalized_category = str(category).strip().lower()

    if normalized_category not in RISK_CATEGORIES:
        raise ValueError(
            f"Unknown risk category: {normalized_category}"
        )

    if normalized_category not in FINDING_DEFINITIONS:
        raise ValueError(
            f"No finding definition exists for category: "
            f"{normalized_category}"
        )

    normalized_score = round(
        max(0.0, min(100.0, float(score))),
        2,
    )

    definition = FINDING_DEFINITIONS[normalized_category]
    severity = determine_severity(normalized_score)

    return {
        "category": normalized_category,
        "finding_type": definition["finding_type"],
        "title": definition["title"],
        "severity": severity,
        "score": normalized_score,
        "description": definition["description"],
        "impact": definition["impact"],
        "mitigation": definition["mitigation"],
        "educational_only": True,
    }


def should_generate_finding(score: float) -> bool:
    """
    Decide whether a category warrants a user-facing finding.

    A category at 20 or below is treated as a low-exposure area and does
    not require a problem finding by default.
    """
    return float(score) > 20


def generate_privacy_findings(
    category_scores: dict[str, float],
) -> list[dict[str, Any]]:
    """
    Generate findings from category scores.

    Findings are sorted from highest severity/highest score to lowest.

    Returns:
        A list of explainable privacy findings.
    """
    configuration = validate_finding_configuration()

    if not configuration["valid"]:
        raise ValueError(
            "Finding configuration is invalid: "
            f"{configuration}"
        )

    validated_category_scores = calculate_category_scores(
        category_scores
    )

    findings = []

    for category in RISK_CATEGORIES:
        score = validated_category_scores[category]

        if should_generate_finding(score):
            findings.append(
                generate_category_finding(
                    category=category,
                    score=score,
                )
            )

    severity_rank = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    findings.sort(
        key=lambda finding: (
            severity_rank[finding["severity"]],
            finding["score"],
        ),
        reverse=True,
    )

    return findings


def generate_findings_from_responses(
    responses: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract features and generate privacy findings directly from
    questionnaire responses.
    """
    feature_result = extract_privacy_features(responses)

    category_scores = calculate_category_scores(
        feature_result["category_averages"]
    )

    findings = generate_privacy_findings(
        category_scores
    )

    severity_summary = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    for finding in findings:
        severity_summary[finding["severity"]] += 1

    return {
        "findings": findings,
        "finding_count": len(findings),
        "severity_summary": severity_summary,
        "category_scores": category_scores,
    }


def get_top_findings(
    findings: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return up to `limit` highest-priority findings.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1.")

    return findings[:limit]


def main() -> None:
    """
    Verify finding configuration.
    """
    result = validate_finding_configuration()

    print("=" * 70)
    print("PRIVACY FINDINGS CONFIGURATION")
    print("=" * 70)
    print(f"Valid: {result['valid']}")
    print(f"Risk categories: {result['category_count']}")
    print(
        "Finding definitions:",
        result["finding_definition_count"],
    )

    if result["missing_categories"]:
        print(
            "Missing categories:",
            result["missing_categories"],
        )

    if result["unknown_categories"]:
        print(
            "Unknown categories:",
            result["unknown_categories"],
        )

    if result["valid"]:
        print("All risk categories have finding definitions.")

    print("=" * 70)


if __name__ == "__main__":
    main()