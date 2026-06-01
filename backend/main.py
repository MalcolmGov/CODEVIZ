"""
Main entry point for CodeViz Backend

Run with:
  python main.py
  
Or with production WSGI server:
  gunicorn wsgi:app
"""

import os
from app import create_app

# Determine environment
ENV = os.getenv('FLASK_ENV', 'development')

# Create app
app = create_app(ENV)

if __name__ == '__main__':
    print(f"🚀 Starting CodeViz Backend ({ENV})")
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('BACKEND_PORT', 8000)),
        debug=(ENV == 'development')
    )
