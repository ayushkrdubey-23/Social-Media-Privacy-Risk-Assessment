"""
Flask application entry point for the
Social Media Privacy Risk Assessment Framework.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from backend.routes.assessment_routes import assessment_bp
from backend.routes.checklist_routes import checklist_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.questionnaire_routes import questionnaire_bp
from backend.utils.database import initialize_database


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env",
    )
)


def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "local-development-secret-change-before-deployment",
    )

    app.config["DEBUG"] = (
        os.getenv(
            "FLASK_DEBUG",
            "false",
        ).lower()
        == "true"
    )

    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://127.0.0.1:5500",
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": frontend_origin,
            }
        },
    )

    initialize_database()

    @app.after_request
    def add_security_headers(response):
        """
        Add basic security and privacy headers to every response.
        """
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"

        return response

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """
        Handle oversized request bodies.
        """
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "REQUEST_TOO_LARGE",
                    "message": (
                        "Request body exceeds the configured "
                        "size limit."
                    ),
                },
            }
        ), 413

    @app.get("/")
    def home():
        """
        Basic project information.
        """
        return jsonify(
            {
                "success": True,
                "project": (
                    "Social Media Privacy Risk Assessment Framework"
                ),
                "status": "running",
            }
        ), 200

    @app.get("/api/health")
    def health():
        """
        Health-check endpoint.
        """
        return jsonify(
            {
                "success": True,
                "status": "healthy",
            }
        ), 200

    @app.get("/api/info")
    def info():
        """
        Basic API information.
        """
        return jsonify(
            {
                "success": True,
                "project": (
                    "Social Media Privacy Risk Assessment Framework"
                ),
                "version": "1.0.0",
                "privacy_mode": (
                    "self-reported and synthetic data only"
                ),
            }
        ), 200

    app.register_blueprint(
        questionnaire_bp
    )

    app.register_blueprint(
        assessment_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        checklist_bp
    )

    return app


app = create_app()


if __name__ == "__main__":
    host = "127.0.0.1"

    port = int(
        os.getenv(
            "PORT",
            "5000",
        )
    )

    app.run(
        host=host,
        port=port,
        debug=app.config["DEBUG"],
    )