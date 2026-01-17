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
# REGISTER FORM (USER INPUT CONTRACT)
# =================================================
# This class does NOT handle:
# ❌ database writes
# ❌ authentication
# ❌ password hashing
#
# This class ONLY defines:
# ✔ what inputs are expected
# ✔ what rules those inputs must satisfy
#
# Interview insight:
# Forms are the FIRST defensive layer against bad input,
# but they are NOT the final authority (DB is).
# =================================================
class RegisterForm(FlaskForm):

    # =================================================
    # CUSTOM FIELD VALIDATION: USERNAME
    # =================================================
    # validate_<fieldname> is discovered AUTOMATICALLY.
    #
    # How Flask-WTF finds this:
    # - Uses Python reflection
    # - Scans for methods named validate_<field>
    #
    # Execution order (important):
    # 1. Built-in validators (Length, DataRequired)
    # 2. Custom validate_<field>()
    #
    # Common confusion:
    # ❌ "Does this run on GET?"
    # ✅ No. Runs ONLY on POST + validate_on_submit().
    #
    # Interview question:
    # Q: Why not rely only on DB unique constraint?
    # A: DB handles race conditions, form handles UX.
    # =================================================
    def validate_username(self, username_to_check):

        # Query DB to check if username already exists
        #
        # Important:
        # This is a READ-only query, not a write.
        user = User.query.filter_by(name=username_to_check.data).first()

        # Raising ValidationError:
        # - Stops validation chain
        # - Attaches error to this field
        # - Automatically exposed via form.errors in template
        if user:
            raise ValidationError(
                'Username already exists! Please try a different username'
            )

    # =================================================
    # CUSTOM FIELD VALIDATION: EMAIL
    # =================================================
    # Triggered because field name == email_address
    #
    # Design principle:
    # - Form validates intent (user input)
    # - DB enforces truth (constraints)
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
    # FORM FIELD DEFINITIONS (DECLARATIVE)
    # =================================================
    # These are CLASS ATTRIBUTES.
    #
    # Flask-WTF metaclass:
    # - Collects these fields
    # - Creates per-request instances
    #
    # Common confusion:
    # ❌ "Are these shared between users?"
    # ✅ No. Each request gets a fresh form instance.
    # =================================================

    # USERNAME FIELD
    # Validation chain:
    # Length → DataRequired → validate_username()
    username = StringField(
        label='User Name:',
        validators=[Length(min=2, max=30), DataRequired()]
    )

    # EMAIL FIELD
    # Email() checks SYNTAX only.
    # It does NOT verify:
    # ❌ domain existence
    # ❌ inbox validity
    email_address = StringField(
        label='Email Address:',
        validators=[Email(), DataRequired()]
    )

    # PASSWORD FIELD
    # PasswordField:
    # - Masks input in browser
    # - Does NOT hash
    #
    # Interview trap:
    # Q: Why not hash password here?
    # A: Security logic belongs to the model.
    password1 = PasswordField(
        label='Password:',
        validators=[Length(min=6), DataRequired()]
    )

    # CONFIRM PASSWORD FIELD
    # EqualTo compares RAW INPUT values.
    # Hash comparison happens later in model.
    password2 = PasswordField(
        label='Confirm Password:',
        validators=[EqualTo('password1'), DataRequired()]
    )

    # SUBMIT BUTTON
    # SubmitField has no validation logic.
    submit = SubmitField(label='Create Account')


# =================================================
# LOGIN FORM (AUTH SHAPE ONLY)
# =================================================
# Purpose:
# - Capture credentials
# - Validate presence
#
# DOES NOT:
# ❌ authenticate
# ❌ hash
# ❌ access DB directly
#
# Interview insight:
# Authentication truth belongs to:
# - Model (password verification)
# - Flask-Login (session handling)
# =================================================
class LoginForm(FlaskForm):

    username = StringField(
        label='User Name:',
        validators=[DataRequired()]
    )

    password = PasswordField(
        label='Password:',
        validators=[DataRequired()]
    )

    submit = SubmitField(label='Sign in')


# =================================================
# PURCHASE / SELL FORMS (ACTION TRIGGERS)
# =================================================
# These forms exist ONLY to:
# - Trigger POST requests
# - Provide CSRF protection
#
# They intentionally have NO fields.
#
# Common confusion:
# ❌ "Why use a form if no input?"
# ✅ CSRF protection + semantic POST intent.
# =================================================
class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')

class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')


# =================================================
# CORE FLASK-WTF CONCEPTS (INTERVIEW GOLD)
# =================================================
#
# 1. Forms define INPUT RULES, not BUSINESS RULES
# 2. validate_on_submit() = POST + CSRF + validators
# 3. Custom validators are discovered by naming convention
# 4. Forms NEVER mutate database state
# 5. Database constraints are the final safety net
#
# REQUEST FLOW:
# Browser
#   → Form (shape + rules)
#   → Route (decision)
#   → Model (truth + mutation)
#   → Database
#
# One-line rule (MEMORIZE):
# "Forms protect UX, models protect integrity."
# =================================================
