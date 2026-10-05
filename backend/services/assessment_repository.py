"""
Privacy-safe SQLite repository for completed assessments.

Only derived assessment information is persisted.

The repository deliberately does NOT save:
- names,
- email addresses,
- phone numbers,
- passwords,
- usernames,
- exact locations,
- private messages,
- raw questionnaire responses.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.services.recommendations_engine import (
    RECOMMENDATION_MAP,
)
from backend.utils.database import (
    get_db_connection,
    initialize_database,
)


VALID_RISK_LEVELS = {
    "LOW",
    "MODERATE",
    "HIGH",
    "CRITICAL",
}

VALID_FINDING_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


def _generate_assessment_id() -> str:
    """
    Generate a non-sequential assessment identifier.

    This identifier does not contain user information.
    """
    return f"ASM-{uuid.uuid4().hex.upper()}"


def _utc_timestamp() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def _validate_assessment_result(
    assessment_result: dict[str, Any],
) -> None:
    """
    Validate the minimum structure required for persistence.
    """
    if not isinstance(assessment_result, dict):
        raise ValueError(
            "Assessment result must be a dictionary."
        )

    if not assessment_result.get("valid"):
        raise ValueError(
            "Only a valid assessment can be persisted."
        )

    assessment = assessment_result.get("assessment")

    if not isinstance(assessment, dict):
        raise ValueError(
            "Assessment result is missing the assessment object."
        )

    risk = assessment.get("risk")

    if not isinstance(risk, dict):
        raise ValueError(
            "Assessment result is missing the risk object."
        )

    overall_score = risk.get("overall_score")
    risk_level = str(
        risk.get("risk_level", "")
    ).strip().upper()

    if overall_score is None:
        raise ValueError(
            "Assessment result is missing overall_score."
        )

    try:
        normalized_score = float(overall_score)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "overall_score must be numeric."
        ) from exc

    if not 0 <= normalized_score <= 100:
        raise ValueError(
            "overall_score must be between 0 and 100."
        )

    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(
            f"Invalid risk level: {risk_level}"
        )

    category_scores = risk.get("category_scores")

    if not isinstance(category_scores, dict):
        raise ValueError(
            "Assessment result is missing category_scores."
        )

    findings = assessment.get("findings", [])

    if not isinstance(findings, list):
        raise ValueError(
            "Assessment findings must be a list."
        )


def save_assessment(
    assessment_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Persist a completed assessment and its derived findings.

    Returns:
        {
            "assessment_id": "...",
            "overall_score": 42.5,
            "risk_level": "HIGH",
            "category_count": 10,
            "finding_count": 3,
            "created_at": "...",
        }
    """
    _validate_assessment_result(
        assessment_result
    )

    initialize_database()

    assessment = assessment_result["assessment"]
    risk = assessment["risk"]

    assessment_id = _generate_assessment_id()
    created_at = _utc_timestamp()

    overall_score = round(
        float(risk["overall_score"]),
        2,
    )

    risk_level = str(
        risk["risk_level"]
    ).strip().upper()

    category_scores = risk["category_scores"]
    findings = assessment["findings"]

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO assessments (
                assessment_id,
                overall_score,
                risk_level,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                assessment_id,
                overall_score,
                risk_level,
                created_at,
            ),
        )

        for category, score in category_scores.items():
            cursor.execute(
                """
                INSERT INTO category_scores (
                    assessment_id,
                    category,
                    score
                )
                VALUES (?, ?, ?)
                """,
                (
                    assessment_id,
                    category,
                    round(float(score), 2),
                ),
            )

        for finding in findings:
            finding_type = str(
                finding.get("finding_type", "")
            ).strip().upper()

            severity = str(
                finding.get("severity", "")
            ).strip().upper()

            description = str(
                finding.get("description", "")
            ).strip()

            category = str(
                finding.get("category", "")
            ).strip().lower()

            if not finding_type:
                raise ValueError(
                    "Finding is missing finding_type."
                )

            if severity not in VALID_FINDING_SEVERITIES:
                raise ValueError(
                    f"Invalid finding severity: {severity}"
                )

            if not category:
                raise ValueError(
                    "Finding is missing category."
                )

            if not description:
                raise ValueError(
                    "Finding is missing description."
                )

            cursor.execute(
                """
                INSERT INTO findings (
                    assessment_id,
                    category,
                    finding_type,
                    severity,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    assessment_id,
                    category,
                    finding_type,
                    severity,
                    description,
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "assessment_id": assessment_id,
        "overall_score": overall_score,
        "risk_level": risk_level,
        "category_count": len(category_scores),
        "finding_count": len(findings),
        "created_at": created_at,
    }


def seed_recommendation_catalog() -> int:
    """
    Populate the static recommendation catalog.

    Recommendations are stored by finding type because they are reusable
    educational guidance, not user-specific personal information.
    """
    initialize_database()

    connection = get_db_connection()

    inserted_count = 0

    try:
        cursor = connection.cursor()

        for finding_type, definition in RECOMMENDATION_MAP.items():
            finding_type_normalized = str(
                finding_type
            ).strip().upper()

            recommendation = str(
                definition["recommendation"]
            ).strip()

            priority = str(
                definition["priority"]
            ).strip().upper()

            cursor.execute(
                """
                SELECT recommendation_id
                FROM recommendations
                WHERE finding_type = ?
                """,
                (finding_type_normalized,),
            )

            existing = cursor.fetchone()

            if existing is not None:
                continue

            cursor.execute(
                """
                INSERT INTO recommendations (
                    finding_type,
                    recommendation,
                    priority
                )
                VALUES (?, ?, ?)
                """,
                (
                    finding_type_normalized,
                    recommendation,
                    priority,
                ),
            )

            inserted_count += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return inserted_count


def get_assessment(
    assessment_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve one persisted assessment and its derived information.

    Raw questionnaire responses are intentionally not returned because
    they are not stored.
    """
    normalized_id = str(
        assessment_id
    ).strip()

    if not normalized_id:
        raise ValueError(
            "assessment_id cannot be empty."
        )

    initialize_database()

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                assessment_id,
                overall_score,
                risk_level,
                created_at
            FROM assessments
            WHERE assessment_id = ?
            """,
            (normalized_id,),
        )

        assessment_row = cursor.fetchone()

        if assessment_row is None:
            return None

        cursor.execute(
            """
            SELECT
                category,
                score
            FROM category_scores
            WHERE assessment_id = ?
            ORDER BY category
            """,
            (normalized_id,),
        )

        category_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                category,
                finding_type,
                severity,
                description
            FROM findings
            WHERE assessment_id = ?
            ORDER BY
                CASE severity
                    WHEN 'CRITICAL' THEN 4
                    WHEN 'HIGH' THEN 3
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 1
                    ELSE 0
                END DESC,
                finding_id ASC
            """,
            (normalized_id,),
        )

        finding_rows = cursor.fetchall()

        return {
            "assessment_id": assessment_row[
                "assessment_id"
            ],
            "overall_score": float(
                assessment_row["overall_score"]
            ),
            "risk_level": assessment_row[
                "risk_level"
            ],
            "created_at": assessment_row[
                "created_at"
            ],
            "category_scores": {
                row["category"]: float(row["score"])
                for row in category_rows
            },
            "findings": [
                {
                    "category": row["category"],
                    "finding_type": row["finding_type"],
                    "severity": row["severity"],
                    "description": row["description"],
                }
                for row in finding_rows
            ],
            "privacy_note": (
                "Raw questionnaire responses and direct personal "
                "identifiers are not stored."
            ),
        }

    finally:
        connection.close()


def get_assessment_recommendations(
    assessment_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve recommendations associated with an assessment.

    Recommendations are resolved from the reusable recommendation catalog
    using the finding types persisted for that assessment.
    """
    normalized_id = str(
        assessment_id
    ).strip()

    if not normalized_id:
        raise ValueError(
            "assessment_id cannot be empty."
        )

    initialize_database()

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                assessment_id
            FROM assessments
            WHERE assessment_id = ?
            """,
            (normalized_id,),
        )

        assessment_row = cursor.fetchone()

        if assessment_row is None:
            return None

        cursor.execute(
            """
            SELECT
                f.category,
                f.finding_type,
                f.severity,
                f.description,
                r.recommendation,
                r.priority
            FROM findings AS f
            LEFT JOIN recommendations AS r
                ON r.finding_type = f.finding_type
            WHERE f.assessment_id = ?
            ORDER BY
                CASE r.priority
                    WHEN 'IMMEDIATE' THEN 3
                    WHEN 'IMPORTANT' THEN 2
                    WHEN 'GOOD PRACTICE' THEN 1
                    ELSE 0
                END DESC,
                CASE f.severity
                    WHEN 'CRITICAL' THEN 4
                    WHEN 'HIGH' THEN 3
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 1
                    ELSE 0
                END DESC,
                f.finding_id ASC
            """,
            (normalized_id,),
        )

        rows = cursor.fetchall()

        recommendations = []

        seen_finding_types = set()

        for row in rows:
            finding_type = row["finding_type"]

            if finding_type in seen_finding_types:
                continue

            seen_finding_types.add(
                finding_type
            )

            recommendation = row["recommendation"]
            priority = row["priority"]

            if not recommendation:
                definition = RECOMMENDATION_MAP.get(
                    finding_type
                )

                if definition:
                    recommendation = (
                        definition["recommendation"]
                    )
                    priority = definition["priority"]

            if not recommendation:
                continue

            recommendations.append(
                {
                    "category": row["category"],
                    "finding_type": finding_type,
                    "severity": row["severity"],
                    "priority": priority,
                    "recommendation": recommendation,
                    "action": (
                        RECOMMENDATION_MAP.get(
                            finding_type,
                            {},
                        ).get("action")
                    ),
                    "educational_only": True,
                }
            )

        return {
            "assessment_id": normalized_id,
            "recommendation_count": len(
                recommendations
            ),
            "recommendations": recommendations,
            "privacy_note": (
                "Recommendations are derived from stored finding "
                "types and do not require raw questionnaire responses."
            ),
        }

    finally:
        connection.close()


def get_assessment_counts() -> dict[str, int]:
    """
    Return basic aggregate assessment counts.
    """
    initialize_database()

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) AS total FROM assessments"
        )

        total = int(
            cursor.fetchone()["total"]
        )

        cursor.execute(
            """
            SELECT
                risk_level,
                COUNT(*) AS count
            FROM assessments
            GROUP BY risk_level
            ORDER BY risk_level
            """
        )

        rows = cursor.fetchall()

        by_risk_level = {
            row["risk_level"]: int(row["count"])
            for row in rows
        }

        return {
            "total_assessments": total,
            "by_risk_level": by_risk_level,
        }

    finally:
        connection.close()


def delete_assessment(
    assessment_id: str,
) -> bool:
    """
    Delete one assessment.

    Foreign-key cascade behavior from the database schema removes
    associated category scores and findings.
    """
    normalized_id = str(
        assessment_id
    ).strip()

    if not normalized_id:
        raise ValueError(
            "assessment_id cannot be empty."
        )

    initialize_database()

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM assessments
            WHERE assessment_id = ?
            """,
            (normalized_id,),
        )

        deleted = cursor.rowcount > 0

        connection.commit()

        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main() -> None:
    """
    Initialize the database and seed the recommendation catalog.
    """
    initialize_database()

    inserted = seed_recommendation_catalog()

    print("=" * 70)
    print("ASSESSMENT REPOSITORY")
    print("=" * 70)
    print("Database initialized successfully.")
    print(
        "Recommendation catalog entries inserted:",
        inserted,
    )
    print(
        "Privacy policy: derived assessment data only."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()