#!/usr/bin/env python
"""
Production run script for Heuristics AI
"""

import os
from app import create_app

# Get configuration
config_name = os.environ.get('FLASK_ENV', 'production')

# Create app instance
app = create_app(config_name)

if __name__ == '__main__':
    # For development
    if config_name == 'development':
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # For production, use gunicorn
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))