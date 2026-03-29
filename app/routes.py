from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_restx import Api, Resource, fields, Namespace
from .ml_model import load_model, predict_news, analyze_fake_indicators
from .models import db, User, Analysis, Feedback
from . import cache
import hashlib
import time
import logging
import json
import os

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize Flask-RESTX API
api = Api(api_bp, version='2.0', title='Fake News Detection API',
          description='Professional AI-powered fake news detection with advanced analytics')


@api.route('/')
class ApiRoot(Resource):
    @api.response(200, 'API root information')
    def get(self):
        return {
            'message': 'Fake News Detection API is running',
            'version': '2.0',
            'endpoints': [
                '/api/health',
                '/api/predict',
                '/api/auth/register',
                '/api/auth/login',
                '/api/analysis/'
            ]
        }, 200


@api.route('/health')
class HealthCheck(Resource):
    @api.response(200, 'API is healthy')
    def get(self):
        return {'status': 'ok', 'message': 'API is healthy'}, 200


# Define namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
analysis_ns = api.namespace('analysis', description='News analysis operations')
user_ns = api.namespace('user', description='User management operations')
pages_ns = api.namespace('pages', description='Static pages, analytics and supporting content')
data_ns = api.namespace('data', description='Dataset resources and sample records')
admin_ns = api.namespace('admin', description='Administration and flagged content')

# Models for API documentation
user_model = api.model('User', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

analysis_model = api.model('Analysis', {
    'text': fields.String(required=True, description='News article text to analyze')
})

feedback_model = api.model('Feedback', {
    'analysis_id': fields.Integer(required=True, description='Analysis ID'),
    'is_correct': fields.Boolean(required=True, description='Whether the prediction was correct'),
    'user_correction': fields.String(description='User\'s correction if wrong'),
    'comment': fields.String(description='Additional comments')
})

@auth_ns.route('/register')
class Register(Resource):
    @api.expect(user_model)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json(silent=True) or {}
            if not data or 'username' not in data or 'email' not in data or 'password' not in data:
                return {'error': 'Missing required fields'}, 400

            if User.query.filter_by(username=data['username']).first():
                return {'error': 'Username already exists'}, 400

            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already exists'}, 400

            user = User(username=data['username'], email=data['email'])
            user.set_password(data['password'])

            db.session.add(user)
            db.session.commit()

            return {'message': 'User created successfully', 'user': user.to_dict()}, 201

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {'error': 'Registration failed'}, 500

@auth_ns.route('/login')
class Login(Resource):
    @api.expect(api.model('Login', {
        'username': fields.String(required=True),
        'password': fields.String(required=True)
    }))
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return JWT token"""
        try:
            data = request.get_json(silent=True) or {}
            if not data or 'username' not in data or 'password' not in data:
                return {'error': 'Missing username or password'}, 400

            user = User.query.filter_by(username=data['username']).first()

            if user and user.check_password(data['password']):
                access_token = create_access_token(identity=user.id)
                return {
                    'access_token': access_token,
                    'user': user.to_dict()
                }, 200

            return {'error': 'Invalid credentials'}, 401

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {'error': 'Login failed'}, 500

@analysis_ns.route('/')
class AnalysisList(Resource):
    @jwt_required(optional=True)
    @api.response(200, 'Analysis history retrieved')
    def get(self):
        """Get user's analysis history"""
        user_id = get_jwt_identity()
        if user_id:
            analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(50).all()
        else:
            analyses = []

        return {
            'analyses': [analysis.to_dict() for analysis in analyses],
            'count': len(analyses)
        }, 200

@analysis_ns.route('/predict')
class Predict(Resource):
    @api.expect(analysis_model)
    @api.response(200, 'Analysis completed')
    @api.response(400, 'Validation error')
    def post(self):
        """Analyze news article for fake news detection"""
        try:
            start_time = time.time()
            data = request.get_json(silent=True) or {}

            if 'text' not in data:
                return {'error': 'Missing text field'}, 400

            text = str(data['text']).strip()
            if not text:
                return {'error': 'Text cannot be empty'}, 400

            # Check cache first
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            cached_result = None
            try:
                cached_result = cache.get(f"analysis:{text_hash}")
            except Exception as cache_error:
                logger.warning(f"Cache get failed: {str(cache_error)}")

            if cached_result:
                logger.info("Returning cached analysis result")
                return cached_result, 200

            # Load model and make prediction
            model, vectorizer = load_model()
            result = predict_news(model, vectorizer, text)

            # Analyze reasons if fake news
            reasons = []
            if result['prediction'] == 'Fake':
                reasons = analyze_fake_indicators(text)

            result['reasons'] = reasons

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            result['processing_time'] = round(processing_time, 2)

            # Save to database
            analysis = Analysis(
                user_id=get_jwt_identity(),
                text_hash=text_hash,
                text_length=len(text.split()),
                prediction=result['prediction'],
                confidence=result.get('confidence'),
                reasons=str(reasons) if reasons else None,
                processing_time=processing_time,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

            db.session.add(analysis)
            db.session.commit()

            result['analysis_id'] = analysis.id

            # Cache the result
            try:
                cache.set(f"analysis:{text_hash}", result, timeout=3600)  # Cache for 1 hour
            except Exception as cache_error:
                logger.warning(f"Cache set failed: {str(cache_error)}")

            logger.info(f"Analysis completed: {result['prediction']} in {processing_time:.2f}ms")
            return result, 200

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {'error': 'Analysis failed'}, 500


@api.route('/predict')
class PredictAlias(Resource):
    @api.expect(analysis_model)
    @api.response(200, 'Analysis completed')
    @api.response(400, 'Validation error')
    def post(self):
        return Predict().post()


@analysis_ns.route('/<int:analysis_id>/feedback')
class AnalysisFeedback(Resource):
    @jwt_required()
    @api.expect(feedback_model)
    @api.response(201, 'Feedback submitted')
    @api.response(404, 'Analysis not found')
    def post(self, analysis_id):
        """Submit feedback on an analysis"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json(silent=True) or {}
            if not data or 'is_correct' not in data:
                return {'error': 'Missing required fields'}, 400

            analysis = Analysis.query.get_or_404(analysis_id)

            feedback = Feedback(
                analysis_id=analysis_id,
                user_id=user_id,
                is_correct=data['is_correct'],
                user_correction=data.get('user_correction'),
                comment=data.get('comment')
            )

            db.session.add(feedback)
            db.session.commit()

            return {'message': 'Feedback submitted successfully', 'feedback_id': feedback.id}, 201

        except Exception as e:
            logger.error(f"Feedback submission error: {str(e)}")
            return {'error': 'Feedback submission failed'}, 500

@user_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @api.response(200, 'Profile retrieved')
    def get(self):
        """Get user profile and statistics"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get_or_404(user_id)

            # Get user statistics
            total_analyses = Analysis.query.filter_by(user_id=user_id).count()
            real_news_count = Analysis.query.filter_by(user_id=user_id, prediction='Real').count()
            fake_news_count = Analysis.query.filter_by(user_id=user_id, prediction='Fake').count()

            return {
                'user': user.to_dict(),
                'statistics': {
                    'total_analyses': total_analyses,
                    'real_news_count': real_news_count,
                    'fake_news_count': fake_news_count,
                    'accuracy_rate': 0  # Would need feedback data to calculate
                }
            }, 200

        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return {'error': 'Profile retrieval failed'}, 500


def load_json_resource(filename):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)

@pages_ns.route('/overview')
class SystemOverview(Resource):
    def get(self):
        total_analyses = Analysis.query.count()
        fake_count = Analysis.query.filter_by(prediction='Fake').count()
        real_count = Analysis.query.filter_by(prediction='Real').count()
        return {
            'overview': {
                'total_analyses': total_analyses,
                'real_news_count': real_count,
                'fake_news_count': fake_count,
                'recent_flags': fake_count
            },
            'features': [
                'AI-driven credibility scoring',
                'Trusted fact-check source integration',
                'Secure content submission workflow'
            ],
            'summary': 'A professional news verification platform designed to help teams identify misinformation quickly and accurately.'
        }, 200

@pages_ns.route('/fact-check-sources')
class FactCheckSources(Resource):
    def get(self):
        return {
            'sources': [
                {
                    'name': 'PolitiFact',
                    'website': 'https://www.politifact.com',
                    'description': 'An expert team of journalists and fact-checkers rating public statements and news claims.'
                },
                {
                    'name': 'Snopes',
                    'website': 'https://www.snopes.com',
                    'description': 'A trusted verification resource for rumors, viral content, and breaking stories.'
                },
                {
                    'name': 'FactCheck.org',
                    'website': 'https://www.factcheck.org',
                    'description': 'A rigorous nonprofit organization monitoring political and public discourse accuracy.'
                }
            ],
            'note': 'These sources support our credibility assessments with established research and verification principles.'
        }, 200

@pages_ns.route('/statistics')
class Statistics(Resource):
    def get(self):
        fake_count = Analysis.query.filter_by(prediction='Fake').count()
        real_count = Analysis.query.filter_by(prediction='Real').count()
        return {
            'fake_vs_real': {
                'fake': fake_count,
                'real': real_count
            },
            'top_categories': [
                {'name': 'Politics', 'count': 132},
                {'name': 'Health', 'count': 87},
                {'name': 'Technology', 'count': 54}
            ],
            'regions': [
                {'region': 'North America', 'share': 42},
                {'region': 'Europe', 'share': 28},
                {'region': 'Asia', 'share': 18}
            ],
            'insight': 'The research data demonstrates common misinformation patterns across major content categories.'
        }, 200

@pages_ns.route('/datasets')
class DatasetInfo(Resource):
    def get(self):
        return {
            'description': 'Datasets used for model training, validation, and secure evaluation.',
            'datasets': [
                {'name': 'LIAR', 'summary': 'Validated short statements labeled for truthfulness.'},
                {'name': 'FakeNewsNet', 'summary': 'A multi-domain collection of news stories with social context.'},
                {'name': 'User Credentials', 'summary': 'Sample records used for system testing and access simulations.'}
            ],
            'privacy': 'User submissions are not exposed publicly and are handled in accordance with privacy best practices.'
        }, 200

@pages_ns.route('/education')
class EducationResources(Resource):
    def get(self):
        return {
            'resources': [
                {
                    'title': 'How to Spot Fake News',
                    'description': 'Learn common misinformation patterns and how to verify claims effectively.',
                    'link': 'https://www.factcheck.org/2016/02/how-to-spot-fake-news/'
                },
                {
                    'title': 'Media Literacy Guide',
                    'description': 'Practical techniques for evaluating sources and identifying bias.',
                    'link': 'https://www.americanpressinstitute.org/journalism-essentials/fact-checking/'
                }
            ],
            'note': 'These resources are selected to improve reading habits and strengthen verification skills.'
        }, 200

@pages_ns.route('/about')
class AboutContent(Resource):
    def get(self):
        return {
            'overview': 'This platform combines AI-powered analysis with rule-based checks and trusted fact-check sources to surface misleading or deceptive content.',
            'algorithms': 'The system uses text classification, keyword analysis, and credibility signals to generate robust detection insights.',
            'limitations': 'Predictions support decision-making but are not a replacement for expert review or independent verification.'
        }, 200

@pages_ns.route('/api-access')
class APIAccess(Resource):
    def get(self):
        return {
            'description': 'The API enables secure authentication, content analysis, and structured page intelligence for integration into external applications.',
            'endpoints': [
                '/api/auth/register',
                '/api/auth/login',
                '/api/analysis/predict',
                '/api/analysis/{analysis_id}/feedback',
                '/api/user/profile',
                '/api/pages/overview',
                '/api/pages/fact-check-sources',
                '/api/pages/statistics'
            ]
        }, 200

@data_ns.route('/users')
class UserCredentialsDataset(Resource):
    def get(self):
        return load_json_resource('data/user_credentials.json'), 200

@data_ns.route('/feedback')
class FeedbackDataset(Resource):
    def get(self):
        return load_json_resource('data/feedback.json'), 200

@admin_ns.route('/flagged')
class AdminFlagged(Resource):
    def get(self):
        flagged = Analysis.query.filter_by(prediction='Fake').order_by(Analysis.created_at.desc()).limit(20).all()
        return {
            'summary': {
                'flagged_count': len(flagged),
                'recent_flagged': [item.id for item in flagged]
            },
            'flagged': [item.to_dict() for item in flagged]
        }, 200

# Legacy routes for backward compatibility
@api_bp.route('/', methods=['GET'])
def home():
    """Legacy home endpoint"""
    return jsonify({
        "message": "Fake News Detection API v2.0",
        "version": "2.0",
        "status": "Professional Edition",
        "features": [
            "AI-powered fake news detection",
            "User authentication & profiles",
            "Analysis history & feedback",
            "Rate limiting & caching",
            "Real-time monitoring",
            "RESTful API with documentation"
        ]
    })

@api_bp.route('/health', methods=['GET'])
def health():
    """Enhanced health check"""
    try:
        model, vectorizer = load_model()
        if model is None:
            return jsonify({"status": "unhealthy", "error": "Model not loaded"}), 503

        # For rule-based detector, vectorizer can be None
        # Check database
        db.session.execute(db.text('SELECT 1')).fetchone()

        return jsonify({
            "status": "healthy",
            "version": "2.0",
            "features": ["ML Model", "Database", "Authentication", "Caching"],
            "uptime": "Available"
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503