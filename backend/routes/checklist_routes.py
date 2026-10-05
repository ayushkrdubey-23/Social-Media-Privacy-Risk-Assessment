"""
Flask routes for the privacy awareness checklist.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from backend.services.privacy_checklist import (
    get_all_checklist_items,
    get_checklist_by_category,
    get_checklist_summary,
)


checklist_bp = Blueprint(
    "checklist",
    __name__,
    url_prefix="/api/privacy-checklist",
)


@checklist_bp.get("")
def get_checklist():
    """
    Return the complete privacy awareness checklist.
    """
    return jsonify(
        {
            "success": True,
            "checklist": get_checklist_summary(),
            "items": get_all_checklist_items(),
        }
    ), 200


@checklist_bp.get("/summary")
def get_checklist_summary_api():
    """
    Return checklist metadata without returning every item.
    """
    return jsonify(
        {
            "success": True,
            "checklist": get_checklist_summary(),
        }
    ), 200


@checklist_bp.get("/category/<category>")
def get_checklist_category(category: str):
    """
    Return checklist items for one category.
    """
    items = get_checklist_by_category(
        category
    )

    if not items:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "CHECKLIST_CATEGORY_NOT_FOUND",
                    "message": (
                        f"Checklist category '{category}' "
                        "was not found."
                    ),
                },
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "category": str(category).strip().lower(),
            "item_count": len(items),
            "items": items,
        }
    ), 200
