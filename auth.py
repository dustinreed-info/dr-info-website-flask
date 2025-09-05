"""
Authentication module for securing analytics endpoints
"""

import os
from flask import request, Response

# Load environment variables from .env file if it exists
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass  # .env file doesn't exist, use default values


class AnalyticsAuth:
    """Authentication handler for analytics dashboard"""
    
    def __init__(self):
        # Analytics authentication credentials
        # Can be set via environment variables for better security
        self.username = os.environ.get('ANALYTICS_USERNAME')
        self.password = os.environ.get('ANALYTICS_PASSWORD')
    
    def check_credentials(self, username, password):
        """Check if username and password are correct"""
        return username == self.username and password == self.password
    
    def authenticate(self):
        """Send 401 response with WWW-Authenticate header"""
        return Response(
            'Authentication required to access analytics dashboard.\n'
            'Please enter your credentials.',
            401,
            {'WWW-Authenticate': 'Basic realm="Analytics Dashboard"'}
        )
    
    def requires_auth(self, f):
        """Decorator to require authentication for analytics routes"""
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_credentials(auth.username, auth.password):
                return self.authenticate()
            return f(*args, **kwargs)
        decorated.__name__ = f.__name__
        return decorated


# Create a global instance for easy importing
analytics_auth = AnalyticsAuth()

# Convenience decorator for easy use
requires_auth = analytics_auth.requires_auth
