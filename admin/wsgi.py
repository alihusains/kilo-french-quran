#!/usr/bin/env python3
"""
WSGI entry point for PythonAnywhere deployment.

This file is used by PythonAnywhere's web app configuration.
"""
import os
import sys
import pathlib

# Add project directories to path
PATH = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(PATH))
sys.path.insert(0, str(PATH.parent))

# Set environment defaults
DATABASE_PATH = str(PATH.parent / 'oc_frenchquran.sqlite')
if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = DATABASE_PATH

if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'

if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

# Verify database exists
if not os.path.exists(os.environ['DATABASE_PATH']):
    print(f"WARNING: Database not found at {os.environ['DATABASE_PATH']}", file=sys.stderr)

from app import app as application

# For WSGI servers
application
