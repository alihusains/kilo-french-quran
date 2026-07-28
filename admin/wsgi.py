#!/usr/bin/env python3
import os
import sys

# PythonAnywhere / WSGI setup
path = '/home/admin/frenchquran/admin'
if path not in sys.path:
    sys.path.insert(0, path)

# Env defaults (override in WSGI config if needed)
if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = os.path.join(path, '..', 'database.sqlite')
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

from app import app as application
