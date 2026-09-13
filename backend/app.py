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
    from backend.routes.appointment_routes import appointment_bp
except ImportError:
    from database.connection import init_db
    from routes.chat_routes import chat_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.appointment_routes import appointment_bp


def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application.

    Args:
        test_config: Optional test configuration mapping.

    Returns:
        Flask: The configured Flask app instance.
    """
    app = Flask(__name__)
    app.secret_key = "neobharat_secret_key_for_testing"

    if test_config:
        app.config.update(test_config)

    # Initialize database tables if not already present
    db_path = app.config.get("DATABASE_PATH")
    init_db(db_path)

    # Register API blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(appointment_bp)
    try:
        from backend.routes.auth_routes import auth_bp
    except ImportError:
        from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": getattr(e, "description", "Bad request")}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
