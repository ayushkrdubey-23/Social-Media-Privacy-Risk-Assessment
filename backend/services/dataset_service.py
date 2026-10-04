"""
Synthetic dataset loading and quality-audit service.

This service works only with the project's synthetic assessment dataset.

It does not access social media platforms and does not process real-user
accounts or direct personal identifiers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.services.questionnaire import get_all_questions
from backend.services.synthetic_data import (
    DEFAULT_OUTPUT_PATH,
    BEHAVIOR_PROFILES,
    validate_generated_dataset,
)


DATASET_PATH = Path(DEFAULT_OUTPUT_PATH)


def load_synthetic_dataset(
    dataset_path: Path | str = DATASET_PATH,
) -> pd.DataFrame:
    """
    Load the synthetic assessment CSV into a pandas DataFrame.

    Raises:
        FileNotFoundError: When the dataset does not exist.
        ValueError: When the dataset fails the project's structural audit.
    """
    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Synthetic dataset not found: {path}"
        )

    dataframe = pd.read_csv(path)

    validation = validate_generated_dataset(dataframe)

    if not validation["valid"]:
        error_text = "; ".join(validation["errors"])
        raise ValueError(
            f"Synthetic dataset validation failed: {error_text}"
        )

    return dataframe


def get_dataset_shape(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    """Return dataset row and column counts."""
    return {
        "records": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
    }


def get_behavior_profile_counts(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    """
    Return counts for each synthetic behavior profile.

    Profiles with zero records are included to keep the structure stable.
    """
    counts = dataframe["behavior_profile"].value_counts().to_dict()

    return {
        profile_name: int(counts.get(profile_name, 0))
        for profile_name in BEHAVIOR_PROFILES
    }


def get_question_response_distribution(
    dataframe: pd.DataFrame,
    question_id: str,
) -> dict[str, int]:
    """
    Return response counts for a single questionnaire question.
    """
    normalized_id = str(question_id).strip().upper()

    question_map = {
        question["id"]: question
        for question in get_all_questions()
    }

    if normalized_id not in question_map:
        raise ValueError(
            f"Unknown questionnaire ID: {normalized_id}"
        )

    response_counts = (
        dataframe[normalized_id]
        .astype(str)
        .str.strip()
        .str.upper()
        .value_counts()
        .to_dict()
    )

    allowed_options = [
        str(option).strip().upper()
        for option in question_map[normalized_id]["options"]
    ]

    return {
        option: int(response_counts.get(option, 0))
        for option in allowed_options
    }


def get_dataset_quality_report(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return a complete quality report for a loaded synthetic dataset.
    """
    validation = validate_generated_dataset(dataframe)
    shape = get_dataset_shape(dataframe)
    profile_counts = get_behavior_profile_counts(dataframe)

    questions = get_all_questions()

    non_null_questions = {}
    for question in questions:
        question_id = question["id"]

        non_null_questions[question_id] = int(
            dataframe[question_id].notna().sum()
        )

    return {
        "valid": validation["valid"],
        "records": shape["records"],
        "columns": shape["columns"],
        "question_count": len(questions),
        "behavior_profile_count": len(BEHAVIOR_PROFILES),
        "behavior_profile_counts": profile_counts,
        "question_response_completeness": non_null_questions,
        "validation_errors": validation["errors"],
    }


def get_dataset_summary(
    dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return a concise summary suitable for future APIs or dashboards.
    """
    questions = get_all_questions()

    return {
        "dataset_name": "Social Media Privacy Synthetic Assessments",
        "dataset_type": "synthetic",
        "records": int(len(dataframe)),
        "columns": int(len(dataframe.columns)),
        "questions": len(questions),
        "categories": len(
            {question["category"] for question in questions}
        ),
        "behavior_profiles": get_behavior_profile_counts(dataframe),
        "date_range": {
            "minimum": str(dataframe["created_at"].min()),
            "maximum": str(dataframe["created_at"].max()),
        },
    }


def print_dataset_report(
    dataframe: pd.DataFrame,
) -> None:
    """Print a human-readable dataset audit report."""
    report = get_dataset_quality_report(dataframe)
    summary = get_dataset_summary(dataframe)

    print("=" * 72)
    print("SOCIAL MEDIA PRIVACY SYNTHETIC DATASET AUDIT")
    print("=" * 72)
    print(f"Dataset type: {summary['dataset_type']}")
    print(f"Records: {summary['records']}")
    print(f"Columns: {summary['columns']}")
    print(f"Questions: {summary['questions']}")
    print(f"Categories: {summary['categories']}")
    print(
        "Behavior profiles:",
        summary["behavior_profiles"],
    )
    print(
        "Date range:",
        summary["date_range"]["minimum"],
        "to",
        summary["date_range"]["maximum"],
    )
    print(f"Validation passed: {report['valid']}")

    if report["validation_errors"]:
        print("\nValidation errors:")

        for error in report["validation_errors"]:
            print(f"- {error}")
    else:
        print("\nValidation errors: none")

    incomplete_questions = [
        question_id
        for question_id, count in report[
            "question_response_completeness"
        ].items()
        if count != report["records"]
    ]

    if incomplete_questions:
        print("\nIncomplete questions:")
        for question_id in incomplete_questions:
            print(f"- {question_id}")
    else:
        print("\nAll 50 questionnaire columns are complete.")

    print("=" * 72)


def main() -> None:
    """Load the default dataset and print its audit report."""
    dataframe = load_synthetic_dataset()
    print_dataset_report(dataframe)


if __name__ == "__main__":
    main()