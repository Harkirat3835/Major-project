from flask import Flask, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from prometheus_flask_exporter import PrometheusMetrics
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
metrics = PrometheusMetrics(app=None)

def create_app(config_name=None):
    app = Flask(__name__, template_folder='../templates')

    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    try:
        cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config['REDIS_URL']})
    except Exception as cache_error:
        app.logger.warning(f"Redis cache init failed: {cache_error}. Falling back to simple cache.")
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    limiter.init_app(app)

    # Initialize Prometheus metrics
    metrics.init_app(app)

    # Register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Web routes
    @app.route('/')
    def index():
        """Serve the main web interface"""
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        """Serve the login page"""
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        """Serve the registration page"""
        return render_template('register.html')

    @app.route('/detect')
    def detect_page():
        """Serve the news detection page"""
        return render_template('detect.html')

    @app.route('/about')
    def about_page():
        """Serve the about project page"""
        return render_template('about.html')

    @app.route('/how-it-works')
    def how_it_works_page():
        """Serve the how it works page"""
        return render_template('how-it-works.html')

    @app.route('/dataset')
    def dataset_page():
        """Serve the dataset information page"""
        return render_template('dataset.html')

    @app.route('/technology')
    def technology_page():
        """Serve the technology stack page"""
        return render_template('technology.html')

    @app.route('/tips')
    def tips_page():
        """Serve the tips for identifying fake news page"""
        return render_template('tips.html')

    @app.route('/contact')
    def contact_page():
        """Serve the contact page"""
        return render_template('contact.html')

    @app.route('/results')
    def results_page():
        """Serve the results and statistics page"""
        return render_template('results.html')

    @app.route('/docs')
    def api_docs():
        """Redirect to API documentation"""
        return render_template('index.html')  # Could create a separate docs page

    # Create database tables
    with app.app_context():
        db.create_all()

    return app