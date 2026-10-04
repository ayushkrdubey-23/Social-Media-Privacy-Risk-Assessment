
import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from the root .env file.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def create_app():
    """
    Application factory for the Social Media Privacy
    Risk Assessment Framework.
    """

    app = Flask(__name__)

    # Basic application configuration.
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-only-change-this-secret"
    )

    app.config["JSON_SORT_KEYS"] = False

    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

    # Configure frontend origins.
    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://127.0.0.1:5500"
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [frontend_origin]
            }
        }
    )

    # Basic security headers.
    @app.after_request
    def add_security_headers(response):

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Cache-Control"] = "no-store"

        return response

    # Root endpoint.
    @app.route("/", methods=["GET"])
    def home():

        return jsonify({
            "success": True,
            "project": "Social Media Privacy Risk Assessment Framework",
            "message": "Privacy assessment backend is running.",
            "version": "1.0.0"
        }), 200

    # Health-check endpoint.
    @app.route("/api/health", methods=["GET"])
    def health_check():

        return jsonify({
            "success": True,
            "status": "healthy",
            "service": "privacy-risk-assessment-backend"
        }), 200

    # Project information endpoint.
    @app.route("/api/info", methods=["GET"])
    def project_info():

        return jsonify({
            "success": True,
            "project_name": "Social Media Privacy Risk Assessment Framework",
            "project_type": "Defensive Cybersecurity",
            "purpose": "Educational social-media privacy risk assessment",
            "data_policy": "Synthetic and voluntarily provided assessment data only",
            "risk_levels": [
                "LOW",
                "MODERATE",
                "HIGH",
                "CRITICAL"
            ]
        }), 200

    return app


# Create application instance.
app = create_app()


if __name__ == "__main__":

    debug_mode = os.getenv(
        "FLASK_DEBUG",
        "false"
    ).lower() == "true"

    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=debug_mode
    )