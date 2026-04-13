from flask import Flask, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from prometheus_flask_exporter import PrometheusMetrics
import os
from redis import Redis
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect

try:
    from flask_mail import Mail
except ModuleNotFoundError:
    class Mail:  # type: ignore[override]
        def init_app(self, app):
            app.logger.warning("Flask-Mail is not installed. Email features are disabled.")

from .utils import seed_demo_users

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
metrics = PrometheusMetrics(app=None)


def _sqlite_schema_out_of_date(app):
    database_uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
    if not database_uri.startswith('sqlite:'):
        return False

    from .models import User, Analysis, Feedback

    inspector = inspect(db.engine)
    expected_columns = {
        'user': {column.name for column in User.__table__.columns},
        'analysis': {column.name for column in Analysis.__table__.columns},
        'feedback': {column.name for column in Feedback.__table__.columns},
    }

    for table_name, required in expected_columns.items():
        if not inspector.has_table(table_name):
            return False
        current_columns = {column['name'] for column in inspector.get_columns(table_name)}
        if not required.issubset(current_columns):
            app.logger.warning(
                "SQLite table '%s' is missing columns: %s",
                table_name,
                ", ".join(sorted(required - current_columns)),
            )
            return True

    return False

def create_app(config_name=None):
    frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
    app = Flask(__name__, static_folder=frontend_dist, static_url_path='', template_folder=frontend_dist)

    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    
    # Cache initialization
    try:
        redis_client = Redis.from_url(app.config['REDIS_URL'], socket_connect_timeout=1, socket_timeout=1)
        redis_client.ping()
        cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config['REDIS_URL']})
        app.logger.info("Redis cache initialized successfully")
    except Exception as cache_error:
        app.logger.warning(f"Redis cache init failed: {cache_error}. Falling back to simple cache.")
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    
    limiter.init_app(app)
    mail.init_app(app)

    # Initialize Prometheus metrics
    metrics.init_app(app)

    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'auth': 'ready',
            'mail': bool(app.config.get('MAIL_USERNAME')),
            'db': True,
            'cache': cache.config['CACHE_TYPE']
        }

    # Serve static files
    from flask import send_from_directory
    @app.route('/assets/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, f'assets/{filename}')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path: str):
        if path.startswith('api/') or path.startswith('assets/'):
            abort(404)
        return send_from_directory(app.static_folder, 'index.html')

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        try:
            if _sqlite_schema_out_of_date(app):
                db.drop_all()
                db.create_all()
            seed_demo_users(app)
        except OperationalError as db_error:
            # Recover automatically from stale local SQLite schemas after model changes.
            if (
                str(app.config.get('SQLALCHEMY_DATABASE_URI', '')).startswith('sqlite:')
                and (
                    'no such column' in str(db_error).lower()
                    or 'has no column named' in str(db_error).lower()
                )
            ):
                app.logger.warning(
                    "SQLite schema is out of date (%s). Recreating local database tables.",
                    db_error,
                )
                db.session.rollback()
                db.drop_all()
                db.create_all()
                seed_demo_users(app)
            else:
                raise
        app.logger.info("Database initialized and demo users seeded")

    return app
