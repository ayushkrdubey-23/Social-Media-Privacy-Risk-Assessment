
import sqlite3
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database directory
DATA_DIR = BASE_DIR / "data"

# SQLite database location
DATABASE_PATH = DATA_DIR / "privacy_assessment.db"


def get_db_connection():
    """
    Create and return a SQLite database connection.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Initialize all database tables.

    Only assessment results and privacy-risk metadata
    are stored. Sensitive personal information is excluded.
    """

    connection = get_db_connection()

    try:

        connection.executescript("""

            CREATE TABLE IF NOT EXISTS assessments (

                assessment_id TEXT PRIMARY KEY,

                overall_score INTEGER NOT NULL
                    CHECK(overall_score BETWEEN 0 AND 100),

                risk_level TEXT NOT NULL
                    CHECK(risk_level IN (
                        'LOW',
                        'MODERATE',
                        'HIGH',
                        'CRITICAL'
                    )),

                created_at TEXT NOT NULL

            );


            CREATE TABLE IF NOT EXISTS category_scores (

                category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,

                assessment_id TEXT NOT NULL,

                category TEXT NOT NULL,

                score INTEGER NOT NULL
                    CHECK(score BETWEEN 0 AND 100),

                FOREIGN KEY(assessment_id)
                    REFERENCES assessments(assessment_id)
                    ON DELETE CASCADE,

                UNIQUE(assessment_id, category)

            );


            CREATE TABLE IF NOT EXISTS findings (

                finding_id INTEGER PRIMARY KEY AUTOINCREMENT,

                assessment_id TEXT NOT NULL,

                category TEXT NOT NULL,

                finding_type TEXT NOT NULL,

                severity TEXT NOT NULL
                    CHECK(severity IN (
                        'LOW',
                        'MODERATE',
                        'HIGH',
                        'CRITICAL'
                    )),

                description TEXT NOT NULL,

                FOREIGN KEY(assessment_id)
                    REFERENCES assessments(assessment_id)
                    ON DELETE CASCADE

            );


            CREATE TABLE IF NOT EXISTS recommendations (

                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,

                finding_type TEXT NOT NULL,

                recommendation TEXT NOT NULL,

                priority TEXT NOT NULL
                    CHECK(priority IN (
                        'IMMEDIATE',
                        'IMPORTANT',
                        'GOOD PRACTICE'
                    ))

            );


            CREATE INDEX IF NOT EXISTS
                idx_category_assessment
                ON category_scores(assessment_id);


            CREATE INDEX IF NOT EXISTS
                idx_findings_assessment
                ON findings(assessment_id);

        """)

        connection.commit()

        print("Database initialized successfully!")

    except sqlite3.Error:

        connection.rollback()
        raise

    finally:

        connection.close()


if __name__ == "__main__":

    initialize_database()

    print(f"Database location: {DATABASE_PATH}")
    