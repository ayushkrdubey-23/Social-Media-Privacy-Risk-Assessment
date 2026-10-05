"""
Dashboard statistics service.

This module calculates aggregate statistics from derived assessment data.

It deliberately does not expose:
- raw questionnaire responses,
- names,
- emails,
- phone numbers,
- usernames,
- passwords,
- exact locations,
- private messages,
- social-media account identifiers.

All dashboard values are aggregate educational statistics.
"""

from __future__ import annotations

from typing import Any

from backend.services.recommendations_engine import (
    PRIORITY_ORDER,
)
from backend.utils.database import (
    get_db_connection,
    initialize_database,
)


RISK_LEVEL_ORDER = [
    "LOW",
    "MODERATE",
    "HIGH",
    "CRITICAL",
]

FINDING_SEVERITY_ORDER = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


def get_dashboard_statistics() -> dict[str, Any]:
    """
    Return aggregate statistics for the dashboard.

    The function reads only derived assessment information.
    """
    initialize_database()

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # ---------------------------------------------------------
        # Overall assessment statistics
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_assessments,
                COALESCE(AVG(overall_score), 0) AS average_score,
                COALESCE(MIN(overall_score), 0) AS minimum_score,
                COALESCE(MAX(overall_score), 0) AS maximum_score
            FROM assessments
            """
        )

        overall_row = cursor.fetchone()

        total_assessments = int(
            overall_row["total_assessments"]
        )

        average_score = round(
            float(overall_row["average_score"]),
            2,
        )

        minimum_score = round(
            float(overall_row["minimum_score"]),
            2,
        )

        maximum_score = round(
            float(overall_row["maximum_score"]),
            2,
        )

        # ---------------------------------------------------------
        # Risk-level distribution
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                risk_level,
                COUNT(*) AS count
            FROM assessments
            GROUP BY risk_level
            """
        )

        risk_rows = cursor.fetchall()

        risk_distribution_raw = {
            row["risk_level"]: int(row["count"])
            for row in risk_rows
        }

        risk_distribution = {
            level: risk_distribution_raw.get(level, 0)
            for level in RISK_LEVEL_ORDER
        }

        # ---------------------------------------------------------
        # Average category scores
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                category,
                ROUND(AVG(score), 2) AS average_score
            FROM category_scores
            GROUP BY category
            ORDER BY category
            """
        )

        category_rows = cursor.fetchall()

        category_averages = {
            row["category"]: float(
                row["average_score"]
            )
            for row in category_rows
        }

        # ---------------------------------------------------------
        # Finding severity distribution
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                severity,
                COUNT(*) AS count
            FROM findings
            GROUP BY severity
            """
        )

        severity_rows = cursor.fetchall()

        severity_distribution_raw = {
            row["severity"]: int(row["count"])
            for row in severity_rows
        }

        finding_severity_distribution = {
            severity: severity_distribution_raw.get(
                severity,
                0,
            )
            for severity in FINDING_SEVERITY_ORDER
        }

        # ---------------------------------------------------------
        # Total findings
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM findings
            """
        )

        total_findings = int(
            cursor.fetchone()["total"]
        )

        # ---------------------------------------------------------
        # Recommendation priority distribution
        #
        # Recommendations are catalog entries associated with
        # finding types. Count distinct findings by priority.
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                r.priority,
                COUNT(*) AS count
            FROM findings AS f
            INNER JOIN recommendations AS r
                ON r.finding_type = f.finding_type
            GROUP BY r.priority
            """
        )

        priority_rows = cursor.fetchall()

        recommendation_priority_raw = {
            row["priority"]: int(row["count"])
            for row in priority_rows
        }

        recommendation_priority_distribution = {
            priority: recommendation_priority_raw.get(
                priority,
                0,
            )
            for priority in PRIORITY_ORDER
        }

        return {
            "dataset": {
                "type": "derived assessment statistics",
                "privacy_safe": True,
            },
            "assessments": {
                "total": total_assessments,
                "average_score": average_score,
                "minimum_score": minimum_score,
                "maximum_score": maximum_score,
                "risk_distribution": risk_distribution,
            },
            "categories": {
                "average_scores": category_averages,
                "category_count": len(category_averages),
            },
            "findings": {
                "total": total_findings,
                "severity_distribution": (
                    finding_severity_distribution
                ),
            },
            "recommendations": {
                "priority_distribution": (
                    recommendation_priority_distribution
                ),
            },
            "privacy_note": (
                "Dashboard statistics contain aggregate derived data "
                "only. Raw questionnaire responses and direct personal "
                "identifiers are not exposed."
            ),
        }

    finally:
        connection.close()


def get_dashboard_summary() -> dict[str, Any]:
    """
    Return a smaller dashboard summary for lightweight consumers.
    """
    statistics = get_dashboard_statistics()

    return {
        "total_assessments": statistics[
            "assessments"
        ]["total"],
        "average_score": statistics[
            "assessments"
        ]["average_score"],
        "risk_distribution": statistics[
            "assessments"
        ]["risk_distribution"],
        "total_findings": statistics[
            "findings"
        ]["total"],
        "category_count": statistics[
            "categories"
        ]["category_count"],
    }


def main() -> None:
    """
    Print a dashboard statistics summary.
    """
    statistics = get_dashboard_statistics()

    print("=" * 70)
    print("PRIVACY DASHBOARD STATISTICS")
    print("=" * 70)
    print(
        "Total assessments:",
        statistics["assessments"]["total"],
    )
    print(
        "Average score:",
        statistics["assessments"]["average_score"],
    )
    print(
        "Risk distribution:",
        statistics["assessments"]["risk_distribution"],
    )
    print(
        "Total findings:",
        statistics["findings"]["total"],
    )
    print(
        "Category count:",
        statistics["categories"]["category_count"],
    )
    print("=" * 70)


if __name__ == "__main__":
    main()