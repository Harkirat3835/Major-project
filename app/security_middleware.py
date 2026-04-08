from flask import request, jsonify
from functools import wraps
import re

def security_headers():
    """Advanced security headers"""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:",
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    }

def rate_limit_ip():
    """Additional IP-based rate limiting"""
    ip = request.remote_addr
    # Implementation would track requests per IP
    return True

def require_https():
    """Force HTTPS in production"""
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        return jsonify({'error': 'HTTPS required'}), 403, {'Location': url}
    return None

def security_wrapper(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check rate limit
        if not rate_limit_ip():
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # HTTPS check
        https_check = require_https()
        if https_check:
            return https_check
        
        resp = f(*args, **kwargs)
        
        # Apply security headers to all responses
        if isinstance(resp, tuple):
            if len(resp) == 3 and isinstance(resp[2], dict):
                resp[2].update(security_headers())
            else:
                resp = resp[0], resp[1], security_headers()
        else:
            resp = resp, 200, security_headers()
        
        return resp
    return decorated_function
