"""
Flask routes for the Social Media Privacy Risk Assessment questionnaire.

These endpoints expose only the educational questionnaire definition.
They do not access social media accounts or collect direct personal data.
"""

from flask import Blueprint, jsonify

from backend.services.questionnaire import (
    get_all_questions,
    get_question_by_id,
    get_questions_by_category,
    get_questionnaire_summary,
)


questionnaire_bp = Blueprint(
    "questionnaire",
    __name__,
    url_prefix="/api/questionnaire",
)


@questionnaire_bp.get("")
def get_questionnaire():
    """
    Return the complete privacy assessment questionnaire.
    """
    summary = get_questionnaire_summary()

    return jsonify(
        {
            "success": True,
            "questionnaire": summary,
            "questions": get_all_questions(),
        }
    ), 200


@questionnaire_bp.get("/summary")
def get_questionnaire_summary_api():
    """
    Return questionnaire metadata without returning all questions.
    """
    return jsonify(
        {
            "success": True,
            "questionnaire": get_questionnaire_summary(),
        }
    ), 200


@questionnaire_bp.get("/question/<question_id>")
def get_question_api(question_id):
    """
    Return one question by its stable question ID.
    """
    question = get_question_by_id(question_id)

    if question is None:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "QUESTION_NOT_FOUND",
                    "message": f"Question '{question_id}' was not found.",
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "question": question,
        }
    ), 200


@questionnaire_bp.get("/category/<category>")
def get_category_questions_api(category):
    """
    Return all questions belonging to one questionnaire category.
    """
    questions = get_questions_by_category(category)

    if not questions:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "CATEGORY_NOT_FOUND",
                    "message": f"Category '{category}' was not found.",
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "category": str(category).strip().lower(),
            "question_count": len(questions),
            "questions": questions,
        }
    ), 200