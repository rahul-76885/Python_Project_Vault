from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.model import User


# -------------------------------------------------
# REGISTER FORM
# -------------------------------------------------
# This class defines the structure of the
# registration form using Flask-WTF.
#
# FlaskForm provides:
# - CSRF protection
# - Form validation support
# - Easy integration with HTML templates
# -------------------------------------------------
class RegisterForm(FlaskForm):
    
    # -------------------------------------------------
    # Custom validation for the "username" field
    # -------------------------------------------------
    # Flask-WTF automatically calls this method when:
    # - The form is submitted
    # - The field name is "username"
    #
    # Naming rule (VERY IMPORTANT):
    # validate_<fieldname>(self, field)
    # -------------------------------------------------
    def validate_username(self, username_to_check):
        
        # Query the database to check
        # if a user with the same username already exists
        user = User.query.filter_by(name=username_to_check.data).first()

        # If a user is found, raise a validation error
        # This stops form submission and adds an error message
        if user:
            raise ValidationError(
                'Username already exists! Please try a different username'
            )

    # -------------------------------------------------
    # Custom validation for the "email_address" field
    # -------------------------------------------------
    # This method is automatically triggered because
    # the field name is "email_address"
    # -------------------------------------------------
    def validate_email_address(self, email_address_to_check):
        
        # Query the database to check
        # if the email address is already registered
        email_address = User.query.filter_by(
            email=email_address_to_check.data
        ).first()

        # If email already exists, raise a validation error
        if email_address:
            raise ValidationError(
                'Email Address already exists! Please try a different email address'
            )

    # Username input field
    # StringField creates a text input (<input type="text">)
    # label is what appears next to / above the input in the form
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    # Email input field
    # This also uses StringField because email is text
    # Validation (like email format) can be added later
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])

    # Password input field
    # PasswordField masks input characters for security
    # (<input type="password">)
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    # Confirm password field
    # Used to ensure user typed the password correctly
    # Usually validated to match password1
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])

    # Submit button
    # Triggers form submission when clicked
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')
