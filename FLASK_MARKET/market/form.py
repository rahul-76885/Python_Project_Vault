from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    Length,
    EqualTo,
    Email,
    DataRequired,
    ValidationError
)
from market.model import User


# =================================================
# REGISTER FORM
# =================================================
# Role of this class:
# - Define INPUT STRUCTURE (fields)
# - Define INPUT RULES (validators)
#
# FlaskForm responsibilities:
# ✔ CSRF protection (per request token)
# ✔ Validation orchestration
# ✔ Binding request data to Python objects
#
# Common confusion:
# ❌ "Does this class store form data?"
# ✅ No. It only defines rules; instances hold data per request.
# =================================================
class RegisterForm(FlaskForm):

    # =================================================
    # FIELD-SPECIFIC CUSTOM VALIDATION (USERNAME)
    # =================================================
    # Naming convention:
    # validate_<fieldname>(self, field)
    #
    # This is NOT magic:
    # Flask-WTF uses reflection to find these methods
    # and attaches them to the field's validation pipeline.
    #
    # Execution timing:
    # - Runs ONLY during form.validate_on_submit()
    # - Runs AFTER built-in validators (Length, DataRequired)
    #
    # Important distinction:
    # - This is APPLICATION-LEVEL validation
    # - Database uniqueness is still enforced separately
    # =================================================
    def validate_username(self, username_to_check):

        # Query database to check existence
        #
        # Common confusion:
        # ❌ "Is this slow? Does it run every time?"
        # ✅ It runs ONLY on form submission, not on page load.
        user = User.query.filter_by(name=username_to_check.data).first()

        # Raising ValidationError:
        # - Stops validation chain for this field
        # - Attaches error message to the field
        #
        # Route logic remains clean and unaware of this rule.
        if user:
            raise ValidationError(
                'Username already exists! Please try a different username'
            )

    # =================================================
    # FIELD-SPECIFIC CUSTOM VALIDATION (EMAIL)
    # =================================================
    # Triggered automatically because field name matches
    # validate_email_address(...)
    #
    # Separation of responsibility:
    # - Form checks user intent
    # - DB constraint handles race conditions
    # =================================================
    def validate_email_address(self, email_address_to_check):

        email_address = User.query.filter_by(
            email=email_address_to_check.data
        ).first()

        if email_address:
            raise ValidationError(
                'Email Address already exists! Please try a different email address'
            )

    # =================================================
    # FORM FIELDS (DECLARATIVE)
    # =================================================
    # These are CLASS ATTRIBUTES, not instance attributes.
    #
    # Flask-WTF uses metaclasses to:
    # - Collect fields
    # - Bind them to form instances at runtime
    # =================================================

    # Username field
    # Length validator:
    # - Prevents too short / too long usernames early
    # DataRequired:
    # - Prevents empty submissions
    #
    # Validation order:
    # Length → DataRequired → validate_username()
    username = StringField(
        label='User Name:',
        validators=[Length(min=2, max=30), DataRequired()]
    )

    # Email field
    # Email():
    # - Validates format ONLY
    # - Does NOT check domain existence
    #
    # Common confusion:
    # ❌ "Email() checks if email exists?"
    # ✅ No. It only checks syntax.
    email_address = StringField(
        label='Email Address:',
        validators=[Email(), DataRequired()]
    )

    # Password field
    # PasswordField:
    # - Masks input
    # - Does NOT hash passwords
    #
    # Hashing happens in the model, not here.
    password1 = PasswordField(
        label='Password:',
        validators=[Length(min=6), DataRequired()]
    )

    # Confirm password field
    # EqualTo:
    # - Compares raw input values
    # - Does NOT compare hashed passwords
    password2 = PasswordField(
        label='Confirm Password:',
        validators=[EqualTo('password1'), DataRequired()]
    )

    # Submit button
    # Has no validation logic
    submit = SubmitField(label='Create Account')


# =================================================
# LOGIN FORM
# =================================================
# Simpler form:
# - No uniqueness checks
# - Authentication happens in routes + models
#
# Design choice:
# ❌ Do NOT verify password here
# ✔ Forms validate shape; models validate truth
# =================================================
class LoginForm(FlaskForm):

    # Username input
    username = StringField(
        label='User Name:',
        validators=[DataRequired()]
    )

    # Password input
    password = PasswordField(
        label='Password:',
        validators=[DataRequired()]
    )

    submit = SubmitField(label='Sign in')


# =================================================
# RESEARCH-LEVEL SUMMARY (MEMORIZE)
# =================================================
#
# 1. Forms define RULES, not DATA
# 2. Validation runs ONLY on submission
# 3. Custom validators attach by naming convention
# 4. Forms do NOT hash or authenticate
# 5. DB constraints are final authority
#
# Mental model:
# Browser → Form → Validators → Route → Model → DB
