"""
Flask routes for aggregate privacy dashboard statistics.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from backend.services.dashboard_service import (
    get_dashboard_statistics,
    get_dashboard_summary,
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


@dashboard_bp.get("/stats")
def dashboard_stats():
    """
    Return complete aggregate dashboard statistics.
    """
    try:
        statistics = get_dashboard_statistics()

    except Exception:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "DASHBOARD_STATS_ERROR",
                    "message": (
                        "Dashboard statistics could not be generated."
                    ),
                },
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "statistics": statistics,
        }
    ), 200


@dashboard_bp.get("/summary")
def dashboard_summary():
    """
    Return a compact dashboard summary.
    """
    try:
        summary = get_dashboard_summary()

    except Exception:
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "DASHBOARD_SUMMARY_ERROR",
                    "message": (
                        "Dashboard summary could not be generated."
                    ),
                },
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "summary": summary,
        }
    ), 200