from flask import Flask, request, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from .security_middleware import security_headers, security_wrapper
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_mail import Mail
from prometheus_flask_exporter import PrometheusMetrics
import os

from .utils import seed_demo_users

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
metrics = PrometheusMetrics(app=None)

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
        cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config['REDIS_URL']})
        app.logger.info("Redis cache initialized successfully")
    except Exception as cache_error:
        app.logger.warning(f"Redis cache init failed: {cache_error}. Falling back to simple cache.")
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    
    limiter.init_app(app)
    mail.init_app(app)
    
    # Custom rate limit storage if Redis available
    if app.config.get('REDIS_URL'):
        from flask_limiter import storage
        from redis import Redis
        limiter.storage = storage.RedisStorage(Redis.from_url(app.config['REDIS_URL']))

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
@security_wrapper
def serve_spa(path: str):
    if path.startswith('api/') or path.startswith('assets/'):
        abort(404)
    response = send_from_directory(app.static_folder, 'index.html')
    response.headers.update(security_headers())
    return response

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        seed_demo_users(app)
        app.logger.info("Database initialized and demo users seeded")

    return app
