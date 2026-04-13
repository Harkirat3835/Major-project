from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource, fields, Namespace
from sqlalchemy import or_
from datetime import datetime, timedelta
from .ml_model import (
    load_model,
    predict_news,
    analyze_fake_indicators,
    extract_text_from_url,
    classify_input_source,
)
from .models import db, User, Analysis, Feedback
from . import cache, limiter
import hashlib
import time
import logging
import json
import os

logger = logging.getLogger(__name__)
limit = limiter.limit

api_bp = Blueprint('api', __name__)


def get_current_user_id():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except Exception:
        return None

    return int(identity) if identity is not None else None

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
    'text': fields.String(description='News article text to analyze'),
    'url': fields.String(description='URL to verify'),
    'source_type': fields.String(description='Optional source type: article, social_media, url'),
})

feedback_model = api.model('Feedback', {
    'analysis_id': fields.Integer(required=True, description='Analysis ID'),
    'is_correct': fields.Boolean(required=True, description='Whether the prediction was correct'),
    'user_correction': fields.String(description='User\'s correction if wrong'),
    'comment': fields.String(description='Additional comments')
})

@auth_ns.route('/register')
class Register(Resource):
    @limit("3 per hour", key_func=get_remote_address)
    @api.expect(user_model)
    @api.response(201, 'User registered successfully')
    @api.response(400, 'Validation error')
    @api.response(409, 'User already exists')
    @api.response(429, 'Rate limit exceeded')
    def post(self):
        """Register new user with password policy validation"""
        try:
            data = request.get_json(silent=True) or {}
            username = data.get('username') or data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not all([username, email, password]):
                return {'error': 'Username, email, and password are required'}, 400

            if len(username.strip()) < 3:
                return {'error': 'Username must be at least 3 characters'}, 400

            if '@' not in email or '.' not in email:
                return {'error': 'Valid email address required'}, 400

            if User.query.filter_by(username=username).first():
                return {'error': 'Username already exists'}, 409

            if User.query.filter_by(email=email).first():
                return {'error': 'Email already registered'}, 409

            # Password policy validation
            policy = current_app.config
            if len(password) < policy['PASSWORD_MIN_LENGTH']:
                return {
                    'error': f'Password must be at least {policy["PASSWORD_MIN_LENGTH"]} characters',
                    'policy': {
                        'min_length': policy['PASSWORD_MIN_LENGTH'],
                        'requires_uppercase': policy['PASSWORD_REQUIRE_UPPERCASE'],
                        'requires_lowercase': policy['PASSWORD_REQUIRE_LOWERCASE'],
                        'requires_digit': policy['PASSWORD_REQUIRE_DIGIT'],
                        'requires_special': policy['PASSWORD_REQUIRE_SPECIAL']
                    }
                }, 400

            import re
            if policy['PASSWORD_REQUIRE_UPPERCASE'] and not re.search(r'[A-Z]', password):
                return {'error': 'Password must contain uppercase letter'}, 400
            if policy['PASSWORD_REQUIRE_LOWERCASE'] and not re.search(r'[a-z]', password):
                return {'error': 'Password must contain lowercase letter'}, 400
            if policy['PASSWORD_REQUIRE_DIGIT'] and not re.search(r'\d', password):
                return {'error': 'Password must contain digit'}, 400
            if policy['PASSWORD_REQUIRE_SPECIAL'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return {'error': 'Password must contain special character (!@#$%^&*(),.?\":{}|<>)'}, 400

            user = User(username=username.strip(), email=email.strip())
            user.set_password(password)
            user.email_verified = True
            db.session.add(user)
            db.session.commit()

            return {
                'message': 'Account created successfully.',
                'user': {
                    **user.to_dict(),
                    'name': user.username.replace('_', ' ').title(),
                },
            }, 201

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            return {'error': 'Registration failed. Please try again.'}, 500

@auth_ns.route('/login')
class Login(Resource):
    @limit("5 per 5 minutes", key_func=get_remote_address)
    @api.expect(api.model('Login', {
        'login': fields.String(required=True, description='Username or email'),
        'password': fields.String(required=True, description='Password')
    }))
    @api.response(200, 'Login successful')
    @api.response(400, 'Validation error')
    @api.response(401, 'Invalid credentials or account locked')
    @api.response(429, 'Rate limit exceeded')
    def post(self):
        """Authenticate user with lockout protection and refresh tokens"""
        try:
            data = request.get_json(silent=True) or {}
            login_value = data.get('login') or data.get('username')
            password = data.get('password')

            if not login_value or not password:
                return {'error': 'Missing username/email or password'}, 400

            user = User.query.filter(
                or_(User.username == login_value, User.email == login_value)
            ).first()

            if not user:
                logger.warning(f"Login attempt for non-existent user: {login_value}")
                return {'error': 'Invalid credentials'}, 401

            if user.is_locked():
                remaining = (user.locked_until - datetime.utcnow()).total_seconds() / 60
                return {
                    'error': f'Account locked due to too many failed attempts. Try again in {remaining:.0f} minutes.'
                }, 401

            if user.check_password(password):
                user.reset_failed_logins()
                db.session.commit()
                
                # Create access and refresh tokens
                from flask_jwt_extended import create_refresh_token
                access_token = create_access_token(
                    identity=str(user.id),
                    expires_delta=timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
                )
                refresh_token = create_refresh_token(
                    identity=str(user.id),
                    expires_delta=timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                )
                
                # Securely store refresh token hash
                user.set_refresh_token(refresh_token)
                db.session.commit()
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        **user.to_dict(),
                        'name': user.username.replace('_', ' ').title(),
                    },
                    'token_type': 'Bearer'
                }, 200

            # Failed login
            if not user:
                logger.warning(f"Login attempt for non-existent user: {login_value}")
                return {'error': 'Invalid credentials'}, 401

            user.increment_failed_login()
            db.session.commit()
            
            logger.warning(f"Failed login attempt for user: {login_value} (attempts: {user.failed_logins})")
            if user.is_locked():
                logger.warning(f"User {login_value} locked due to excessive failed logins")
            
            return {'error': 'Invalid credentials'}, 401

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {'error': 'Login failed'}, 500

@auth_ns.route('/verify')
class Verify(Resource):
    @jwt_required()
    @limit("60 per minute", key_func=get_remote_address)
    @api.response(200, 'Token verified')
    @api.response(401, 'Invalid token')
    def get(self):
        user = db.session.get(User, get_current_user_id())
        if not user:
            return {'error': 'User not found'}, 404

        user_data = user.to_dict()
        user_data['name'] = user.username.replace('_', ' ').title()
        return {'user': user_data}, 200

@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @limit("20 per hour", key_func=get_remote_address)
    @api.response(200, 'Tokens refreshed')
    @api.response(401, 'Invalid refresh token')
    def post(self):
        """Refresh access token using refresh token with rotation"""
        try:
            current_user_id = int(get_jwt_identity())
            user = db.session.get(User, current_user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            refresh_token = request.json.get('refresh_token') if request.is_json else None
            
            if not refresh_token or not user.verify_refresh_token(refresh_token):
                return {'error': 'Invalid refresh token'}, 401
            
            # Rotate tokens - generate new ones
            from flask_jwt_extended import create_access_token, create_refresh_token
            new_access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
            )
            new_refresh_token = create_refresh_token(
                identity=str(user.id),
                expires_delta=timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            )
            
            # Store new refresh token hash (single-use old token)
            user.set_refresh_token(new_refresh_token)
            db.session.commit()
            
            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'token_type': 'Bearer',
                'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            }, 200
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {'error': 'Token refresh failed'}, 500

@analysis_ns.route('/')
class AnalysisList(Resource):
    @jwt_required(optional=True)
    @api.response(200, 'Analysis history retrieved')
    def get(self):
        """Get user's analysis history"""
        user_id = get_current_user_id()
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
            current_user_id = None

            text = str(data.get('text', '') or '').strip()
            url = str(data.get('url', '') or '').strip()
            source_type = str(data.get('source_type', '') or '').strip().lower() or None

            if request.headers.get('Authorization', '').startswith('Bearer '):
                current_user_id = get_current_user_id()

            if not text and not url:
                return {'error': 'Please provide article text or a URL to analyze.'}, 400

            if not url and text and classify_input_source(text) == 'url':
                url = text
                text = ''

            if url:
                try:
                    text = extract_text_from_url(url)
                except Exception as fetch_error:
                    logger.warning(f"URL extraction failed: {fetch_error}")
                    return {
                        'error': 'Unable to extract content from the URL. Please provide article text directly or verify the URL.'
                    }, 400
                source_type = 'url'

            if not text:
                return {'error': 'No analysis text available after extraction.'}, 400

            source_type = source_type or classify_input_source(text)
            text_hash = hashlib.sha256((url or text).encode()).hexdigest()

            cached_result = None
            try:
                cached_result = cache.get(f"analysis:{text_hash}")
            except Exception as cache_error:
                logger.warning(f"Cache get failed: {str(cache_error)}")

            if cached_result:
                logger.info("Returning cached analysis result")
                return cached_result, 200

            model, vectorizer = load_model()
            result = predict_news(model, vectorizer, text, source_type=source_type)

            reasons = []
            if result['prediction'] == 'Fake':
                reasons = analyze_fake_indicators(text, source_type=source_type)

            result['reasons'] = reasons
            result['source_type'] = source_type
            result['source_url'] = url if url else None
            result['text_preview'] = text[:280] + ('...' if len(text) > 280 else '')

            processing_time = (time.time() - start_time) * 1000
            result['processing_time'] = round(processing_time, 2)

            analysis = Analysis(
                user_id=current_user_id,
                text_hash=text_hash,
                text_length=len(text.split()),
                source_type=source_type,
                source_url=url if url else None,
                text_preview=result['text_preview'],
                prediction=result['prediction'],
                confidence=result.get('confidence'),
                reasons=json.dumps(reasons) if reasons else None,
                processing_time=processing_time,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

            db.session.add(analysis)
            db.session.commit()

            result['analysis_id'] = analysis.id

            try:
                cache.set(f"analysis:{text_hash}", result, timeout=3600)  # Cache for 1 hour
            except Exception as cache_error:
                logger.warning(f"Cache set failed: {str(cache_error)}")

            logger.info(f"Analysis completed: {result['prediction']} in {processing_time:.2f}ms")
            return result, 200

        except Exception as e:
            logger.exception("Analysis error")
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
            user_id = get_current_user_id()
            data = request.get_json(silent=True) or {}
            if not data or 'is_correct' not in data:
                return {'error': 'Missing required fields'}, 400

            analysis = Analysis.query.get_or_404(analysis_id)

            existing_feedback = None
            if user_id is not None:
                existing_feedback = Feedback.query.filter_by(
                    analysis_id=analysis_id,
                    user_id=user_id
                ).first()

            if existing_feedback:
                existing_feedback.is_correct = data['is_correct']
                existing_feedback.user_correction = data.get('user_correction')
                existing_feedback.comment = data.get('comment')
                feedback = existing_feedback
                status_code = 200
                message = 'Feedback updated successfully'
            else:
                feedback = Feedback(
                    analysis_id=analysis_id,
                    user_id=user_id,
                    is_correct=data['is_correct'],
                    user_correction=data.get('user_correction'),
                    comment=data.get('comment')
                )
                db.session.add(feedback)
                status_code = 201
                message = 'Feedback submitted successfully'

            db.session.commit()

            return {
                'message': message,
                'feedback_id': feedback.id,
                'feedback': feedback.to_dict(),
            }, status_code

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
            user_id = get_current_user_id()
            user = db.session.get(User, user_id)
            if not user:
                return {'error': 'User not found'}, 404

            # Get user statistics
            total_analyses = Analysis.query.filter_by(user_id=user_id).count()
            real_news_count = Analysis.query.filter_by(user_id=user_id, prediction='Real').count()
            fake_news_count = Analysis.query.filter_by(user_id=user_id, prediction='Fake').count()

            return {
                'user': {
                    **user.to_dict(),
                    'name': user.username.replace('_', ' ').title(),
                },
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


@user_ns.route('/history')
class UserHistory(Resource):
    @jwt_required()
    @api.response(200, 'User analysis history retrieved')
    def get(self):
        user_id = get_current_user_id()
        analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(50).all()
        return {'history': [analysis.to_dict() for analysis in analyses]}, 200


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
