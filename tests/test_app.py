import pytest
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.ml_model import clean_text, analyze_fake_indicators

class TestFakeNewsDetector:

    def setup_method(self):
        """Setup test fixtures"""
        test_db = Path(__file__).resolve().parents[1] / 'instance' / 'test.db'
        if test_db.exists():
            try:
                test_db.unlink()
            except PermissionError:
                pass
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_endpoint(self):
        """Test API docs endpoint is available"""
        response = self.client.get('/api/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        assert response.status_code in [200, 503]  # May fail if model not loaded

    def test_login_and_verify_flow(self):
        """Test login returns a usable JWT and verify accepts it."""
        response = self.client.post('/api/auth/login', json={
            'login': 'admin@truthguard.ai',
            'password': 'Admin@1234'
        })
        assert response.status_code == 200

        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'admin@truthguard.ai'

        verify_response = self.client.get(
            '/api/auth/verify',
            headers={'Authorization': f"Bearer {data['access_token']}"}
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.get_json()
        assert verify_data['user']['email'] == 'admin@truthguard.ai'

    def test_predict_endpoint_validation(self):
        """Test prediction endpoint input validation"""
        # Test missing JSON
        response = self.client.post('/api/predict')
        assert response.status_code == 400

        # Test missing text field
        response = self.client.post('/api/predict', json={})
        assert response.status_code == 400

        # Test empty text
        response = self.client.post('/api/predict', json={'text': ''})
        assert response.status_code == 400

    def test_predict_endpoint_classifies_article_text(self):
        """Test prediction endpoint can classify direct article text."""
        response = self.client.post('/api/predict', json={
            'text': (
                "According to Reuters, election officials certified the results after a full "
                "recount and independent observers confirmed the process. The report cited "
                "public filings and official statements from the commission."
            )
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['prediction'] == 'Real'
        assert data['source_type'] == 'article'

    def test_predict_endpoint_classifies_url_content(self):
        """Test prediction endpoint can fetch and classify URL content."""
        article_html = (
            "<html><body><article>"
            "<p>According to Reuters, the ministry confirmed the policy after a public briefing.</p>"
            "<p>Officials said the decision followed a documented review process and published data.</p>"
            "</article></body></html>"
        ).encode('utf-8')

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(article_html)

            def log_message(self, format, *args):
                return

        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            url = f'http://127.0.0.1:{server.server_port}/'
            response = self.client.post('/api/predict', json={'url': url})
            assert response.status_code == 200
            data = response.get_json()
            assert data['prediction'] == 'Real'
            assert data['source_type'] == 'url'
            assert data['source_url'] == url
        finally:
            server.shutdown()
            thread.join(timeout=2)

    def test_clean_text_function(self):
        """Test text cleaning function"""
        # Test basic cleaning
        text = "Hello!!! This is a TEST."
        cleaned = clean_text(text)
        assert cleaned == "hello this is a test"

        # Test with invalid input
        with pytest.raises(ValueError):
            clean_text(123)

    def test_analyze_fake_indicators(self):
        """Test fake news indicator analysis"""
        # Test sensational language
        text = "Shocking news! Unbelievable discovery!"
        reasons = analyze_fake_indicators(text)
        assert len(reasons) > 0
        assert any("sensational" in reason.lower() for reason in reasons)

        # Test conspiracy language
        text = "Deep state conspiracy revealed!"
        reasons = analyze_fake_indicators(text)
        assert any("conspiracy" in reason.lower() for reason in reasons)

        # Test normal text
        text = "According to Reuters, the president visited the country today."
        reasons = analyze_fake_indicators(text)
        # Should have fewer or no reasons for legitimate text
        assert len(reasons) <= 2  # May still flag lack of sources

if __name__ == '__main__':
    pytest.main([__file__])
