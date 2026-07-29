#!/usr/bin/env python3
"""
Flask application entry point.
Run this file directly to start the admin server.
"""
import os
import sys

# Ensure the project root is on the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Validate database exists before starting
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'oc_frenchquran.sqlite')

# Set defaults if not set
if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = DB_PATH
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

# Check database exists
if not os.path.exists(os.environ['DATABASE_PATH']):
    print(f"ERROR: Database not found at {os.environ['DATABASE_PATH']}")
    print("Please run 'python build_database.py' first, or set DATABASE_PATH environment variable.")
    sys.exit(1)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5001'))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print('Starting Quran Admin...')
    print(f'Database: {os.environ["DATABASE_PATH"]}')
    print(f'Port: {port}')
    print(f'Debug: {debug}')
    print(f'Go to http://localhost:{port}')
    
    app.run(host='0.0.0.0', port=port, debug=debug)
