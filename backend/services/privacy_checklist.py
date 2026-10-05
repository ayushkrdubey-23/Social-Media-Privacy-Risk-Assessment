"""
Privacy awareness checklist.

This module provides general privacy and security awareness guidance.
It is independent of individual assessment results.

The checklist does not:
- request personal information,
- access social media accounts,
- inspect private profiles,
- scrape platforms,
- track users,
- guarantee security or privacy outcomes.
"""

from __future__ import annotations

from copy import deepcopy


PRIVACY_CHECKLIST = [
    {
        "id": "CHECK-001",
        "category": "profile",
        "title": "Review profile visibility",
        "action": (
            "Set profile visibility to the smallest audience that "
            "matches your needs."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-002",
        "category": "profile",
        "title": "Review profile discovery settings",
        "action": (
            "Check whether unknown people can easily discover your "
            "profile through platform search or suggestions."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-003",
        "category": "personal_information",
        "title": "Restrict sensitive profile fields",
        "action": (
            "Limit the visibility of sensitive profile-information "
            "categories and remove unnecessary fields."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-004",
        "category": "location",
        "title": "Review location permissions",
        "action": (
            "Disable location permissions for social media apps when "
            "they are not necessary."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-005",
        "category": "location",
        "title": "Avoid unnecessary real-time location sharing",
        "action": (
            "Avoid publicly sharing your current location or routine "
            "when it is not needed."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-006",
        "category": "content",
        "title": "Check audience before posting",
        "action": (
            "Review the audience selector before publishing posts, "
            "photos, or videos."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-007",
        "category": "content",
        "title": "Review older public content",
        "action": (
            "Audit older posts and media for unnecessary public "
            "exposure."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-008",
        "category": "connections",
        "title": "Review connection requests",
        "action": (
            "Check unfamiliar connection or follower requests before "
            "accepting them."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-009",
        "category": "connections",
        "title": "Audit existing connections",
        "action": (
            "Periodically review connections and remove suspicious or "
            "unnecessary accounts."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-010",
        "category": "tagging",
        "title": "Enable tag review",
        "action": (
            "Use tag-review controls where the platform provides them."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-011",
        "category": "tagging",
        "title": "Restrict mentions",
        "action": (
            "Limit who can mention or reference your account where "
            "platform controls allow it."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-012",
        "category": "account_security",
        "title": "Use a strong unique password",
        "action": (
            "Use a strong password that is unique to the account."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-013",
        "category": "account_security",
        "title": "Enable multi-factor authentication",
        "action": (
            "Enable multi-factor authentication using a suitable "
            "supported method."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-014",
        "category": "account_security",
        "title": "Review active sessions",
        "action": (
            "Periodically review logged-in devices and terminate "
            "sessions you do not recognize."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-015",
        "category": "account_security",
        "title": "Review recovery options",
        "action": (
            "Keep account recovery methods current and protected."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-016",
        "category": "third_party_apps",
        "title": "Review connected applications",
        "action": (
            "Audit applications connected to your social media account."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-017",
        "category": "third_party_apps",
        "title": "Remove unused third-party access",
        "action": (
            "Revoke permissions for applications that you no longer use."
        ),
        "priority": "IMPORTANT",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-018",
        "category": "third_party_apps",
        "title": "Review requested permissions",
        "action": (
            "Check whether an application really needs the permissions "
            "it requests."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-019",
        "category": "social_engineering",
        "title": "Treat unexpected links cautiously",
        "action": (
            "Avoid opening unexpected links from unfamiliar or "
            "unverified messages."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-020",
        "category": "social_engineering",
        "title": "Verify unusual requests independently",
        "action": (
            "Confirm unusual requests for money or information using "
            "a separate trusted channel."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-021",
        "category": "social_engineering",
        "title": "Protect verification codes",
        "action": (
            "Never share passwords, one-time passwords, recovery codes, "
            "or authentication codes with others."
        ),
        "priority": "IMMEDIATE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-022",
        "category": "digital_footprint",
        "title": "Review your public digital footprint",
        "action": (
            "Periodically review the information about you that is "
            "intentionally visible online."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-023",
        "category": "digital_footprint",
        "title": "Review unused accounts",
        "action": (
            "Identify old accounts and secure or close them when "
            "appropriate."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
    {
        "id": "CHECK-024",
        "category": "digital_footprint",
        "title": "Review repeated public identifiers",
        "action": (
            "Consider how reusing the same public username across "
            "services can link otherwise separate online profiles."
        ),
        "priority": "GOOD PRACTICE",
        "completed_by_default": False,
    },
]


VALID_PRIORITIES = {
    "IMMEDIATE",
    "IMPORTANT",
    "GOOD PRACTICE",
}


def get_all_checklist_items() -> list[dict]:
    """
    Return a copy of the complete checklist.
    """
    return deepcopy(PRIVACY_CHECKLIST)


def get_checklist_by_category(
    category: str,
) -> list[dict]:
    """
    Return checklist items for one category.
    """
    normalized_category = (
        str(category)
        .strip()
        .lower()
    )

    return [
        deepcopy(item)
        for item in PRIVACY_CHECKLIST
        if item["category"] == normalized_category
    ]


def get_checklist_summary() -> dict:
    """
    Return checklist metadata and category counts.
    """
    category_counts: dict[str, int] = {}

    for item in PRIVACY_CHECKLIST:
        category = item["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    priority_counts = {
        "IMMEDIATE": 0,
        "IMPORTANT": 0,
        "GOOD PRACTICE": 0,
    }

    for item in PRIVACY_CHECKLIST:
        priority = item["priority"]

        if priority in priority_counts:
            priority_counts[priority] += 1

    return {
        "checklist_name": (
            "Social Media Privacy Awareness Checklist"
        ),
        "item_count": len(PRIVACY_CHECKLIST),
        "category_count": len(category_counts),
        "category_counts": category_counts,
        "priority_counts": priority_counts,
        "educational_only": True,
    }


def validate_checklist() -> dict:
    """
    Validate checklist structure.
    """
    errors = []

    ids = [
        item["id"]
        for item in PRIVACY_CHECKLIST
    ]

    if len(ids) != len(set(ids)):
        errors.append(
            "Checklist contains duplicate IDs."
        )

    for item in PRIVACY_CHECKLIST:
        required_fields = {
            "id",
            "category",
            "title",
            "action",
            "priority",
            "completed_by_default",
        }

        missing_fields = required_fields - set(item)

        if missing_fields:
            errors.append(
                f"{item.get('id', 'UNKNOWN')} is missing: "
                + ", ".join(sorted(missing_fields))
            )

        priority = item.get("priority")

        if priority not in VALID_PRIORITIES:
            errors.append(
                f"{item.get('id', 'UNKNOWN')} has invalid priority "
                f"'{priority}'."
            )

        if not isinstance(
            item.get("completed_by_default"),
            bool,
        ):
            errors.append(
                f"{item.get('id', 'UNKNOWN')} has an invalid "
                "completed_by_default value."
            )

    return {
        "valid": not errors,
        "item_count": len(PRIVACY_CHECKLIST),
        "category_count": len(
            {
                item["category"]
                for item in PRIVACY_CHECKLIST
            }
        ),
        "errors": errors,
    }


def main() -> None:
    """
    Verify and summarize the checklist.
    """
    validation = validate_checklist()
    summary = get_checklist_summary()

    print("=" * 70)
    print("PRIVACY AWARENESS CHECKLIST")
    print("=" * 70)
    print("Valid:", validation["valid"])
    print("Items:", summary["item_count"])
    print("Categories:", summary["category_count"])
    print("Priorities:", summary["priority_counts"])

    if validation["errors"]:
        print("\nErrors:")
        for error in validation["errors"]:
            print("-", error)
    else:
        print("Checklist validation passed.")

    print("=" * 70)


if __name__ == "__main__":
    main()