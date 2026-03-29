#!/usr/bin/env python3
"""
Fake News Detection API - Main Application Entry Point
"""

import os
import sys
from app import create_app
from app.utils import setup_logging, download_nltk_data, ensure_directories, validate_environment

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()

    # Ensure directories exist
    ensure_directories()

    # Download NLTK data
    download_nltk_data()

    # Validate environment
    validate_environment()

    # Create and run app
    app = create_app()

    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    print(f"Starting Fake News Detection API on http://{host}:{port}")
    print("API Documentation: http://localhost:5000/api/")
    print("Health Check: http://localhost:5000/api/health")

    app.run(host=host, port=port, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')

if __name__ == '__main__':
    main()
