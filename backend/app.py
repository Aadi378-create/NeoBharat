"""Flask application for BharatPay AI backend.

Phase 1 provides the backend foundation:
- SQLite connection & initialization
- Simple GET /health endpoint
"""

from flask import Flask, jsonify

try:
    from backend.database.connection import init_db
    from backend.routes.chat_routes import chat_bp
    from backend.routes.dashboard_routes import dashboard_bp
except ImportError:
    from database.connection import init_db
    from routes.chat_routes import chat_bp
    from routes.dashboard_routes import dashboard_bp


def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application.

    Args:
        test_config: Optional test configuration mapping.

    Returns:
        Flask: The configured Flask app instance.
    """
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    # Initialize database tables if not already present
    db_path = app.config.get("DATABASE_PATH")
    init_db(db_path)

    # Register API blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
