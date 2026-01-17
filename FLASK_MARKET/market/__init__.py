from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# =================================================
# FLASK APPLICATION INSTANCE (PROCESS-LEVEL)
# =================================================
# app = Flask(__name__)
#
# CORE CONCEPT (VERY IMPORTANT):
# This line executes ONCE when the Python process starts,
# NOT per request and NOT per user.
#
# Common beginner confusion:
# ❌ "Is a new app created for every request?"
# ✅ No. One Flask app instance serves ALL requests.
#
# Why __name__?
# Flask uses it to:
# - Resolve the root path of the application
# - Locate templates/ and static/ folders
# - Support relative imports and extensions
#
# Interview question:
# Q: What happens if you hardcode the app name?
# A: Breaks modularity, testing, and reuse.
# =================================================
app = Flask(__name__)

# =================================================
# DATABASE CONFIGURATION (APPLICATION CONFIG)
# =================================================
# app.config is a GLOBAL configuration registry.
# Extensions read values from it at initialization.
#
# SQLALCHEMY_DATABASE_URI explains:
# - Which database engine to use
# - Where the database is located
#
# sqlite:///market.db
# ├─ sqlite  → database engine
# ├─ ///     → project root directory
# └─ market.db → database file
#
# Research note:
# SQLite is file-based:
# ✔ Easy to use
# ✘ Not suitable for high concurrency or production scale
# =================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

# =================================================
# SECRET KEY (ROOT OF TRUST)
# =================================================
# SECRET_KEY is one of the MOST CRITICAL settings.
#
# Used for:
# - Signing session cookies
# - CSRF protection (Flask-WTF)
# - Flash messages
#
# Security guarantee:
# If the SECRET_KEY changes:
# ❗ ALL existing sessions become invalid
#
# Interview question:
# Q: Why not hardcode this in production?
# A: Source code leaks = session forgery risk.
#
# Best practice:
# ✔ Use environment variables in production
# =================================================
app.config['SECRET_KEY'] = '78fa206b019df59a56e8017d'  # os.urandom(8).hex()

# =================================================
# EXTENSION INITIALIZATION: BCRYPT
# =================================================
# bcrypt = Bcrypt(app)
#
# What this does:
# - Attaches password hashing utilities to the app
# - Does NOT hash anything yet
#
# Important distinction:
# ❌ Hashing does NOT happen here
# ✅ Hashing happens later inside model methods
#
# Research insight:
# In large applications:
# - Extensions are created WITHOUT app
# - Initialized later via init_app(app)
# =================================================
bcrypt = Bcrypt(app)

# =================================================
# DATABASE INITIALIZATION: SQLALCHEMY
# =================================================
# db = SQLAlchemy(app)
#
# What this sets up:
# - ORM layer
# - Connection handling
# - Session management
#
# Common confusion:
# ❌ "Is db.session global?"
# ✅ No. db.session is REQUEST-SCOPED.
#
# Each request gets its own transaction context.
# =================================================
db = SQLAlchemy(app)

# =================================================
# LOGIN MANAGER (AUTHENTICATION SYSTEM)
# =================================================
# LoginManager wires Flask-Login into the app.
#
# Responsibilities:
# - Session-based authentication
# - Injects current_user into every request
# - Handles unauthorized access
#
# login_view:
# - Endpoint name (NOT URL)
# - Used when @login_required blocks access
#
# login_message_category:
# - Category used for flash messages
#
# Interview question:
# Q: Where is login state stored?
# A: In a signed session cookie (user_id only).
# =================================================
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'

# =================================================
# ROUTE IMPORT (ORDER IS CRITICAL)
# =================================================
# WHY import routes at the BOTTOM?
#
# routes.py requires:
# - app
# - db
# - login_manager
# - bcrypt
#
# If imported earlier:
# ❌ app/db not defined yet
# ❌ circular import error
#
# Python execution model:
# - Files execute top → bottom
# - Imports run immediately
# =================================================
from market import routes

# =================================================
# ROLE OF __init__.py (ARCHITECTURE)
# =================================================
# This file turns "market/" into a Python PACKAGE.
#
# Architectural responsibilities:
# - Application bootstrap
# - Extension wiring
# - Central object registry
#
# Enables clean imports:
# from market import app, db, bcrypt
#
# Interview concept:
# This is the "Application Instance Pattern".
# The scalable evolution is the "Application Factory Pattern".
# =================================================

# =================================================
# HIGH-LEVEL LOGIN FLOW (INTERVIEW GOLD)
# =================================================
#
# 1. User submits login form
# 2. Route validates credentials
# 3. login_user(user) is called
# 4. Flask-Login stores user.id in session
# 5. Session cookie is signed using SECRET_KEY
# 6. On every request:
#    - Flask-Login reads session
#    - Calls user_loader(user_id)
#    - Rebuilds User object
#    - Assigns it to current_user
#
# IMPORTANT:
# - Browser NEVER stores full user data
# - Only a signed identifier is stored
# =================================================

# =================================================
# ONE-LINE CORE FLASK RULE (MEMORIZE)
# =================================================
# "Flask app and extensions are created once;
# routes run per request; users are reconstructed per request."
# =================================================
