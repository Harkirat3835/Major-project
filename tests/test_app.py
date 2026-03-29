import pytest
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.ml_model import clean_text, analyze_fake_indicators

class TestFakeNewsDetector:

    def setup_method(self):
        """Setup test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_endpoint(self):
        """Test home endpoint returns correct response"""
        response = self.client.get('/api/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        assert response.status_code in [200, 503]  # May fail if model not loaded

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