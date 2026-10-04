"""
Synthetic assessment dataset generator.

This module creates fictional questionnaire responses for development,
testing, demonstrations, charts, and future model/risk-engine work.

IMPORTANT:
- No real people are represented.
- No social media accounts are accessed.
- No passwords, emails, phone numbers, exact locations, private messages,
  names, usernames, or other direct identifiers are generated.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from backend.services.questionnaire import get_all_questions


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = (
    BASE_DIR / "data" / "social_media_privacy_assessments.csv"
)

DEFAULT_RECORD_COUNT = 1200
DEFAULT_RANDOM_SEED = 20261004


# ---------------------------------------------------------------------
# Synthetic behavioral personas
# ---------------------------------------------------------------------

BEHAVIOR_PROFILES = {
    "privacy_conscious": {
        "safe_response_probability": 0.90,
    },
    "privacy_balanced": {
        "safe_response_probability": 0.68,
    },
    "exposure_prone": {
        "safe_response_probability": 0.38,
    },
    "high_exposure": {
        "safe_response_probability": 0.16,
    },
}


# ---------------------------------------------------------------------
# Preferred safer response for each question
# ---------------------------------------------------------------------
#
# These values are used ONLY to create varied synthetic data.
# They are not the final risk-scoring logic.
#
SAFE_RESPONSES: Dict[str, str] = {
    "Q001": "PRIVATE",
    "Q002": "PRIVATE",
    "Q003": "PRIVATE",
    "Q004": "YES",
    "Q005": "YES",

    "Q006": "PRIVATE",
    "Q007": "PRIVATE",
    "Q008": "PRIVATE",
    "Q009": "YES",
    "Q010": "YES",

    "Q011": "DISABLED",
    "Q012": "YES",
    "Q013": "YES",
    "Q014": "PRIVATE",
    "Q015": "YES",

    "Q016": "PRIVATE",
    "Q017": "YES",
    "Q018": "YES",
    "Q019": "YES",
    "Q020": "YES",

    "Q021": "NO",
    "Q022": "YES",
    "Q023": "YES",
    "Q024": "PRIVATE",
    "Q025": "YES",

    "Q026": "ENABLED",
    "Q027": "ENABLED",
    "Q028": "NO",
    "Q029": "YES",
    "Q030": "YES",

    "Q031": "YES",
    "Q032": "ENABLED",
    "Q033": "YES",
    "Q034": "YES",
    "Q035": "YES",

    "Q036": "YES",
    "Q037": "YES",
    "Q038": "YES",
    "Q039": "YES",
    "Q040": "YES",

    "Q041": "YES",
    "Q042": "YES",
    "Q043": "YES",
    "Q044": "YES",
    "Q045": "PRIVATE",

    "Q046": "YES",
    "Q047": "YES",
    "Q048": "YES",
    "Q049": "YES",
    "Q050": "YES",
}


def _validate_configuration(questions: List[dict]) -> None:
    """
    Validate that the synthetic generator configuration matches the
    current questionnaire definition.
    """
    question_ids = {question["id"] for question in questions}

    if len(question_ids) != len(questions):
        raise ValueError("Questionnaire contains duplicate question IDs.")

    missing_safe_responses = question_ids - set(SAFE_RESPONSES)
    if missing_safe_responses:
        raise ValueError(
            "Missing safe-response configuration for: "
            + ", ".join(sorted(missing_safe_responses))
        )

    unknown_safe_responses = set(SAFE_RESPONSES) - question_ids
    if unknown_safe_responses:
        raise ValueError(
            "SAFE_RESPONSES contains unknown question IDs: "
            + ", ".join(sorted(unknown_safe_responses))
        )

    for question in questions:
        question_id = question["id"]
        safe_response = SAFE_RESPONSES[question_id]
        allowed_options = {
            str(option).strip().upper()
            for option in question["options"]
        }

        if safe_response not in allowed_options:
            raise ValueError(
                f"Safe response '{safe_response}' is not valid for "
                f"{question_id}."
            )


def _choose_response(
    question: dict,
    safe_response_probability: float,
    rng: np.random.Generator,
) -> str:
    """
    Choose one synthetic response.

    The configured safe response is selected with a persona-dependent
    probability. Other valid responses are distributed randomly.
    """
    question_id = question["id"]

    options = [
        str(option).strip().upper()
        for option in question["options"]
    ]

    safe_response = SAFE_RESPONSES[question_id]

    if rng.random() < safe_response_probability:
        return safe_response

    alternative_options = [
        option for option in options
        if option != safe_response
    ]

    if not alternative_options:
        return safe_response

    return str(rng.choice(alternative_options))


def _generate_created_at(
    index: int,
    rng: np.random.Generator,
) -> str:
    """
    Create a deterministic synthetic timestamp.

    The timestamps represent fictional assessment creation events and
    contain no information about real people.
    """
    start_time = datetime(
        2026,
        1,
        1,
        9,
        0,
        0,
        tzinfo=timezone.utc,
    )

    day_offset = int(rng.integers(0, 273))
    minute_offset = int(rng.integers(0, 24 * 60))

    timestamp = start_time + timedelta(
        days=day_offset,
        minutes=minute_offset,
        seconds=index % 60,
    )

    return timestamp.isoformat()


def generate_synthetic_dataset(
    record_count: int = DEFAULT_RECORD_COUNT,
    random_seed: int = DEFAULT_RANDOM_SEED,
    output_path: Path | str = DEFAULT_OUTPUT_PATH,
) -> pd.DataFrame:
    """
    Generate and save a synthetic social-media privacy dataset.

    Args:
        record_count: Number of synthetic assessments to create.
        random_seed: Seed for reproducible generation.
        output_path: Destination CSV path.

    Returns:
        The generated pandas DataFrame.
    """
    if record_count < 1000:
        raise ValueError(
            "record_count must be at least 1000 for this project."
        )

    questions = get_all_questions()
    _validate_configuration(questions)

    rng = np.random.default_rng(random_seed)

    profile_names = list(BEHAVIOR_PROFILES.keys())
    profile_weights = [0.25, 0.35, 0.25, 0.15]

    selected_profiles = rng.choice(
        profile_names,
        size=record_count,
        p=profile_weights,
    )

    records = []

    for index, behavior_profile in enumerate(selected_profiles, start=1):
        profile_config = BEHAVIOR_PROFILES[str(behavior_profile)]

        record = {
            "synthetic_assessment_id": f"SYN-{index:05d}",
            "behavior_profile": str(behavior_profile),
            "created_at": _generate_created_at(index, rng),
        }

        for question in questions:
            record[question["id"]] = _choose_response(
                question=question,
                safe_response_probability=profile_config[
                    "safe_response_probability"
                ],
                rng=rng,
            )

        records.append(record)

    dataframe = pd.DataFrame(records)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        output_file,
        index=False,
        encoding="utf-8",
    )

    return dataframe


def validate_generated_dataset(dataframe: pd.DataFrame) -> dict:
    """
    Validate the generated dataset structure and values.

    Returns:
        A validation summary dictionary.
    """
    questions = get_all_questions()
    expected_question_ids = [question["id"] for question in questions]

    expected_columns = [
        "synthetic_assessment_id",
        "behavior_profile",
        "created_at",
        *expected_question_ids,
    ]

    actual_columns = list(dataframe.columns)

    errors: List[str] = []

    if len(dataframe) < 1000:
        errors.append(
            f"Dataset contains only {len(dataframe)} records; "
            "at least 1000 are required."
        )

    if len(set(actual_columns)) != len(actual_columns):
        errors.append("Dataset contains duplicate column names.")

    if actual_columns != expected_columns:
        errors.append(
            "Dataset columns do not match the expected questionnaire "
            "schema."
        )

    if not dataframe["synthetic_assessment_id"].is_unique:
        errors.append("Synthetic assessment IDs are not unique.")

    if dataframe["synthetic_assessment_id"].isna().any():
        errors.append("Synthetic assessment IDs contain missing values.")

    if dataframe["behavior_profile"].isna().any():
        errors.append("Behavior profiles contain missing values.")

    expected_profiles = set(BEHAVIOR_PROFILES)

    unknown_profiles = (
        set(dataframe["behavior_profile"].dropna().astype(str))
        - expected_profiles
    )

    if unknown_profiles:
        errors.append(
            "Unknown synthetic behavior profiles: "
            + ", ".join(sorted(unknown_profiles))
        )

    question_lookup = {
        question["id"]: question
        for question in questions
    }

    for question_id in expected_question_ids:
        allowed_values = {
            str(option).strip().upper()
            for option in question_lookup[question_id]["options"]
        }

        observed_values = set(
            dataframe[question_id]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid_values = observed_values - allowed_values

        if invalid_values:
            errors.append(
                f"{question_id} contains invalid values: "
                + ", ".join(sorted(invalid_values))
            )

        missing_count = int(dataframe[question_id].isna().sum())

        if missing_count:
            errors.append(
                f"{question_id} contains {missing_count} missing values."
            )

    # Explicit privacy check for column names.
    forbidden_terms = {
        "name",
        "email",
        "phone",
        "password",
        "address",
        "message",
        "username",
        "exact_location",
        "ip_address",
    }

    suspicious_columns = []

    for column in actual_columns:
        normalized_column = column.lower()

        if any(
            forbidden_term in normalized_column
            for forbidden_term in forbidden_terms
        ):
            suspicious_columns.append(column)

    if suspicious_columns:
        errors.append(
            "Potentially sensitive columns detected: "
            + ", ".join(sorted(suspicious_columns))
        )

    return {
        "valid": not errors,
        "errors": errors,
        "record_count": len(dataframe),
        "column_count": len(actual_columns),
        "question_count": len(expected_question_ids),
        "profile_counts": (
            dataframe["behavior_profile"]
            .value_counts()
            .to_dict()
        ),
    }


def print_dataset_summary(
    dataframe: pd.DataFrame,
    output_path: Path | str,
) -> None:
    """Print a concise human-readable generation summary."""
    validation = validate_generated_dataset(dataframe)

    print("=" * 70)
    print("Synthetic Social Media Privacy Dataset")
    print("=" * 70)
    print(f"Output file: {Path(output_path).resolve()}")
    print(f"Records: {validation['record_count']}")
    print(f"Columns: {validation['column_count']}")
    print(f"Questions: {validation['question_count']}")
    print(f"Validation passed: {validation['valid']}")
    print(f"Behavior profiles: {validation['profile_counts']}")
    print("=" * 70)

    if validation["errors"]:
        print("Validation errors:")
        for error in validation["errors"]:
            print(f"- {error}")
    else:
        print("No validation errors detected.")


def main() -> None:
    """Generate the default project dataset."""
    dataframe = generate_synthetic_dataset()

    print_dataset_summary(
        dataframe=dataframe,
        output_path=DEFAULT_OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()
    