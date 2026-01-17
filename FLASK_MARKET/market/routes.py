# =================================================
# APPLICATION & DATABASE IMPORTS
# =================================================
# app and db are created ONCE when Flask starts.
# They are NOT recreated per request.
#
# Common confusion:
# ❌ "Is app/db created again for every user?"
# ✅ No. Flask loads modules once; requests reuse them.
#
# Why import from package (__init__.py)?
# ✔ Single source of truth
# ✔ Prevents multiple app instances
# ✔ Required for large/scalable applications
from market import app, db

# =================================================
# REQUEST–RESPONSE UTILITIES
# =================================================
# Flask automatically provides request context per request.
# These utilities DO NOT store state.
from flask import render_template, redirect, url_for, flash, request

# =================================================
# ORM MODELS
# =================================================
# Models represent TABLE STRUCTURE, not rows.
# Each query creates NEW Python objects.
from market.model import Item, User

# =================================================
# FORMS
# =================================================
# Forms are recreated PER REQUEST.
#
# Common confusion:
# ❌ "Why not reuse form object?"
# ✅ Forms bind request-specific data → reuse causes bugs.
from market.form import (
    RegisterForm,
    LoginForm,
    PurchaseItemForm,
    SellItemForm
)

# =================================================
# FLASK-LOGIN HELPERS
# =================================================
# Flask-Login stores ONLY user_id in session.
# current_user is reconstructed EVERY request.
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

# =================================================
# IMPORTANT CONCEPT: current_user
# =================================================
# INTERVIEW QUESTION:
# Q: What is current_user?
#
# ANSWER:
# - It is NOT a variable
# - It is a PROXY object
#
# On every request:
# session["user_id"] → load_user(user_id) → User object
#
# If user is not logged in:
# current_user → AnonymousUser
#
# You NEVER manually pass user_id.
# Flask-Login does it automatically.
# =================================================


# =================================================
# HOME PAGE ROUTE
# =================================================
# ROUTE ≠ FUNCTION CALL
#
# This function runs ONLY when:
# - URL matches
# - HTTP method matches
#
# Flask does NOT execute this at startup.
# =================================================
@app.route('/')
@app.route('/home')
def home_page():
    # render_template:
    # - Loads HTML
    # - Injects context variables
    # - Returns Response object
    #
    # No DB access here:
    # ✔ Fast
    # ✔ Scalable
    return render_template('home.html')


# =================================================
# MARKET PAGE (GET + POST)
# =================================================
# login_required:
# - Runs BEFORE route function
# - Checks current_user.is_authenticated
# - Redirects if user is anonymous
#
# INTERVIEW QUESTION:
# Q: How does login_required work?
# A: Decorator + request context + current_user
# =================================================
@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():

    # -------------------------------------------------
    # FORM CREATION
    # -------------------------------------------------
    # New form per request
    purchase_form = PurchaseItemForm()

    # =================================================
    # POST REQUEST → BUY ITEM
    # =================================================
    if request.method == 'POST':

        # -------------------------------------------------
        # request.form.get()
        # -------------------------------------------------
        # INTERVIEW QUESTION:
        # Q: Why use request instead of print()?
        #
        # ANSWER:
        # - print() prints to server console
        # - request.form reads HTTP payload sent by browser
        #
        # Browser → HTTP → Flask → request.form
        purchased_item = request.form.get('purchased_item')

        # -------------------------------------------------
        # WHY QUERY AGAIN AFTER GETTING VALUE?
        # -------------------------------------------------
        # INTERVIEW QUESTION:
        # Q: We already got purchased_item. Why query again?
        #
        # ANSWER:
        # - purchased_item is STRING data (name)
        # - We need FULL Item object to:
        #   ✔ access price
        #   ✔ change ownership
        #   ✔ call model methods
        #
        # Forms send DATA, not OBJECTS.
        p_item_object = Item.query.filter_by(
            name=purchased_item
        ).first()

        if p_item_object:

            # -------------------------------------------------
            # AUTHORIZATION CHECK
            # -------------------------------------------------
            # WHY in model?
            # - Budget belongs to User
            # - Business rule belongs to model
            if current_user.can_purchase(p_item_object):

                # -------------------------------------------------
                # MODEL METHOD CALL
                # -------------------------------------------------
                # INTERVIEW QUESTION:
                # Q: How does route know buy() exists?
                #
                # ANSWER:
                # - p_item_object is an Item instance
                # - buy() is defined on Item class
                # - Python resolves it via object method lookup
                #
                # Flask does NOTHING magical here.
                p_item_object.buy(current_user)

                flash(
                    f"Congratulations! You purchased {p_item_object.name} "
                    f"for {p_item_object.price}$",
                    category='success'
                )
            else:
                flash(
                    f"Unfortunately, you don't have enough money "
                    f"to purchase {p_item_object.name}!",
                    category='danger'
                )

        # -------------------------------------------------
        # POST-REDIRECT-GET (PRG PATTERN)
        # -------------------------------------------------
        # Prevents:
        # - Duplicate purchases
        # - Browser resubmission on refresh
        return redirect(url_for('market_page'))

    # =================================================
    # GET REQUEST → SHOW ITEMS
    # =================================================
    if request.method == 'GET':

        # Only show unowned items
        items = Item.query.filter_by(owner=None)

        return render_template(
            'market.html',
            items=items,
            purchase_form=purchase_form
        )

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