# Import the Flask application instance and database object
# These are created once when the application starts (process-level),
# NOT per request.
#
# Common confusion:
# ❌ "Is app/db created again on every request?"
# ✅ No. Flask loads modules once; requests reuse these objects.
#
# Why import from package (__init__.py) instead of creating here?
# ✔ Single source of truth
# ✔ Prevents multiple app instances
# ✔ Avoids subtle bugs in large applications
from market import app, db

# Flask utilities used inside request-response cycle
# These are stateless helpers; Flask injects request context automatically
from flask import render_template, redirect, url_for, flash

# ORM models
# Models represent database tables, NOT individual rows
# Each query returns NEW Python objects mapped to DB rows
from market.model import Item, User

# WTForms classes
# Forms are recreated per request to bind fresh request data
# ❌ Never reuse form instances across requests
from market.form import RegisterForm, LoginForm

# Flask-Login session helpers
# These work by storing ONLY user_id in session (not full user object)
from flask_login import login_user, logout_user, login_required


# =================================================
# HOME PAGE ROUTE
# =================================================
# ROUTE ≠ FUNCTION CALL
#
# Route function is executed ONLY when:
# - A request hits the given URL
# - HTTP method matches
#
# Flask does NOT run this code at startup.
# =================================================
@app.route('/')
@app.route('/home')
def home_page():
    # render_template():
    # - Loads HTML
    # - Injects context variables
    # - Returns a Response object
    #
    # No database access here by design:
    # ✔ Keeps landing page fast
    # ✔ Avoids unnecessary DB load
    return render_template('home.html')


# =================================================
# MARKET PAGE ROUTE (AUTHENTICATED)
# =================================================
# login_required:
# - Executes BEFORE the route function
# - Redirects to login view if user is anonymous
#
# Research insight:
# This is implemented via decorators + request context,
# NOT by wrapping code manually inside the function.
# =================================================
@app.route('/market')
@login_required
def market_page():

    # ORM Query Explanation:
    # Item.query.all()
    # - Builds SQL
    # - Executes it
    # - Maps each row → new Item instance
    #
    # Common confusion:
    # ❌ "Are these the same Item objects every time?"
    # ✅ No. New Python objects are created per query.
    items = Item.query.all()

    # Data flow principle:
    # Backend decides WHAT data exists
    # Template decides HOW data looks
    return render_template('market.html', items=items)


# =================================================
# REGISTER ROUTE
# =================================================
# Handles BOTH:
# - GET  → show form
# - POST → process submission
#
# Why same route?
# ✔ HTTP semantics
# ✔ Cleaner mental model
# ✔ Easier testing
# =================================================
@app.route('/register', methods=['GET', 'POST'])
def register_page():

    # New form instance per request
    #
    # Common confusion:
    # ❌ "Why recreate form every time?"
    # ✅ Forms bind request-specific data; reuse causes data leakage
    form = RegisterForm()

    # validate_on_submit():
    # Internally checks:
    # - request.method == POST
    # - CSRF token
    # - field validators
    #
    # This abstracts multiple checks into one safe call
    if form.validate_on_submit():

        # User object here is a transient Python object
        # It does NOT exist in DB until committed
        user_to_create = User(
            name=form.username.data,
            email=form.email_address.data,
            password=form.password1.data
        )

        # db.session:
        # - Tracks pending changes
        # - Is request-scoped (cleaned after request ends)
        db.session.add(user_to_create)

        # Commit boundary:
        # ✔ Writes to DB
        # ✔ Assigns primary key (id)
        #
        # Research note:
        # Until commit, rollback is possible.
        db.session.commit()

        # login_user():
        # Stores ONLY user_id in session cookie
        # User object is reloaded on next request
        login_user(user_to_create)

        flash(
            f"Account created successfully! You are now logged in as {user_to_create.name}",
            category='success'
        )

        # Redirect-after-POST pattern (PRG)
        # Prevents duplicate inserts on browser refresh
        return redirect(url_for('market_page'))

    # Validation errors handling
    #
    # Why loop manually?
    # ✔ Allows granular control over UI messages
    # ✔ Keeps templates logic-free
    if form.errors:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, category='danger')

    return render_template('register.html', form=form)


# =================================================
# LOGIN ROUTE
# =================================================
# Authentication is a READ operation:
# - No DB writes
# - Only session mutation
# =================================================
@app.route('/login', methods=['GET', 'POST'])
def login_page():

    form = LoginForm()

    if form.validate_on_submit():

        # Query returns:
        # - User instance if found
        # - None otherwise
        #
        # .first() is preferred over .one()
        # because it avoids exceptions
        attempted_user = User.query.filter_by(
            name=form.username.data
        ).first()

        # Password check:
        # Happens inside model to:
        # ✔ Centralize security logic
        # ✔ Allow future algorithm changes
        #
        # Route should NOT know hashing details
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)

            flash(
                f'Success! You are logged in as: {attempted_user.name}',
                category='success'
            )

            return redirect(url_for('market_page'))

        else:
            # Intentionally vague error message
            # Research-backed security practice:
            # Avoid user enumeration attacks
            flash(
                'Username and password are not match! Please try again',
                category='danger'
            )

    return render_template('login.html', form=form)


# =================================================
# LOGOUT ROUTE
# =================================================
# logout_user():
# - Clears user_id from session
# - Does NOT delete user data
#
# Session ≠ Database
# =================================================
@app.route('/logout')
def logout_page():

    logout_user()

    flash("You have been logged out!", category='info')

    return redirect(url_for("home_page"))


# Short explanation (for your understanding)

# Routes → Frontend
# Anything you pass in render_template() (for example form=form) is directly available in 
# Jinja.

# current_user → Frontend
# Flask-Login injects current_user automatically on every request after rebuilding it from
#  the database.

# Flash messages → Frontend
# flash() stores messages in the session, and get_flashed_messages() retrieves and clears
#  them for display.

# One-line revision note (save this)

# Templates do not fetch data themselves; they only display data coming from routes, 
# current_user, and flashed messages.


# -------------------------------------------------
# CORE FLASK CONCEPTS (REVISION NOTES)
# -------------------------------------------------

# Routes → Backend Controllers
# Routes control:
# - data flow
# - authentication
# - response rendering

# Templates → Presentation Only
# Templates NEVER:
# - query database
# - modify data
# - perform authentication

# current_user → Auto-injected
# Flask-Login rebuilds current_user on every request
# using session-stored user_id

# Flash messages → Temporary feedback
# Stored in session and removed after being displayed once

# One-line rule (MEMORIZE THIS):
# "Templates display data; routes decide what data exists."

# Request → Route → ORM → Template → Response