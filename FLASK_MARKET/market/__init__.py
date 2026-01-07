from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# -------------------------------------------------
# Create the Flask application instance
# __name__ tells Flask where this file is located,
# which helps Flask find templates, static files,
# and other resources correctly
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# DATABASE CONFIGURATION
# -------------------------------------------------
# SQLALCHEMY_DATABASE_URI tells SQLAlchemy:
# 1. Which database engine to use (sqlite)
# 2. Where the database file is located
#
# 'sqlite:///market.db' means:
# sqlite      -> database engine
# ///         -> current project directory
# market.db  -> database file name
#
# If market.db does not exist, it will be created
# automatically when db.create_all() is called
# -------------------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

# -------------------------------------------------
# SECRET KEY CONFIGURATION
# -------------------------------------------------
# SECRET_KEY is used by Flask for:
# - CSRF protection (Flask-WTF forms)
# - Session security
# - Flash messages
#
# This key should be:
# - Random
# - Kept secret
# - Stored in environment variables in production
# -------------------------------------------------
app.config['SECRET_KEY'] = '78fa206b019df59a56e8017d'

# -------------------------------------------------
# Initialize SQLAlchemy
# -------------------------------------------------
# This connects the Flask app with the database
# and allows us to define models using db.Model
# -------------------------------------------------
db = SQLAlchemy(app)

# -------------------------------------------------
# Import routes AFTER app and db are created
# -------------------------------------------------
# This avoids circular import errors:
# routes.py needs 'app' and 'db',
# so they must exist before importing routes
# -------------------------------------------------
from market import routes

# -------------------------------------------------
# This file makes the 'market' directory a PACKAGE
# -------------------------------------------------
# A Python package allows us to:
# - Organize code into multiple files
# - Import app, db, models, routes cleanly
# - Avoid writing everything in one large file
#
# Without __init__.py:
# - Python would NOT recognize this folder
# - Imports like `from market import app` would fail
# -------------------------------------------------
