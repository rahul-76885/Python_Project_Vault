from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# =================================================
# FLASK APPLICATION INSTANCE (PROCESS-LEVEL)
# =================================================
# app = Flask(__name__)
#
# VERY IMPORTANT MENTAL MODEL:
# This line runs ONCE when the Python process starts,
# NOT on every request.
#
# Common confusion:
# ❌ "Is a new app created per user/request?"
# ✅ No. One app instance serves ALL requests.
#
# Why __name__?
# Flask uses it to:
# - Locate templates/
# - Locate static/
# - Resolve relative paths
#
# Hardcoding a name breaks modularity and testing.
# =================================================
app = Flask(__name__)

# =================================================
# DATABASE CONFIGURATION (APPLICATION CONFIG)
# =================================================
# app.config is a global configuration registry
# Extensions read from it at initialization time.
#
# SQLALCHEMY_DATABASE_URI explains:
# - Which DB engine
# - Where DB lives
#
# sqlite:///market.db
# ├─ sqlite  → engine
# ├─ ///     → project root (relative path)
# └─ market.db → file
#
# Research note:
# SQLite is file-based:
# ✔ Simple
# ✘ Not for high concurrency
# =================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

# =================================================
# SECRET KEY (ROOT OF TRUST)
# =================================================
# SECRET_KEY is CRITICAL for security.
#
# Used for:
# - Signing session cookies
# - CSRF tokens
# - Flash messages
#
# If SECRET_KEY changes:
# ❗ ALL active sessions become invalid
#
# Common beginner mistake:
# ❌ Hardcoding SECRET_KEY in production
# ✔ Use environment variables
#
# os.urandom example shown for learning only.
# =================================================
app.config['SECRET_KEY'] = '78fa206b019df59a56e8017d'  # os.urandom(8).hex()

# =================================================
# EXTENSION INITIALIZATION (BCRYPT)
# =================================================
# Bcrypt(app):
# - Registers hashing utilities with this app
# - Stateless between requests
#
# Hashing does NOT happen here;
# this only wires the extension.
#
# Research insight:
# In larger apps, extensions are often created
# WITHOUT app and later initialized via init_app().
# =================================================
bcrypt = Bcrypt(app)

# =================================================
# DATABASE INITIALIZATION (SQLALCHEMY)
# =================================================
# SQLAlchemy(app):
# - Binds ORM to Flask app
# - Reads DB config
# - Manages sessions per request
#
# Common confusion:
# ❌ "Is db.session global?"
# ✅ No. It is scoped to the current request context.
#
# Models inherit from db.Model AFTER this.
# =================================================
db = SQLAlchemy(app)

# =================================================
# LOGIN MANAGER (AUTHENTICATION LAYER)
# =================================================
# LoginManager handles:
# - Session-based authentication
# - current_user injection
# - Unauthorized redirects
#
# login_view:
# - Endpoint name (NOT URL)
# - Used when @login_required fails
#
# login_message_category:
# - Controls flash message styling
# =================================================
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'

# =================================================
# ROUTE IMPORT (ORDER MATTERS)
# =================================================
# WHY import routes at the BOTTOM?
#
# routes.py needs:
# - app
# - db
# - extensions
#
# If imported earlier:
# ❌ Circular import error
#
# Python execution order:
# Top → Bottom → One time only
# =================================================
from market import routes

# =================================================
# PACKAGE ROLE OF __init__.py
# =================================================
# This file turns "market/" into a Python package.
#
# Architectural role:
# - Central bootstrap point
# - Holds shared objects (app, db, bcrypt)
#
# Enables:
# from market import app, db
#
# Research note:
# This is an "application instance" pattern.
# App Factory pattern is the scalable evolution.
# =================================================
