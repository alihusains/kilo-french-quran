#!/usr/bin/env python3
import os
import sys

# PythonAnywhere / WSGI setup
import pathlib
PATH = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(PATH))
sys.path.insert(0, str(PATH.parent))

# Env defaults (override in WSGI config if needed)
if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = str(PATH.parent / 'oc_frenchquran.sqlite')
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

from app import app as application
