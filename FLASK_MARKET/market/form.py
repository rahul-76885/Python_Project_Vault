from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, Email, DataRequired, EqualTo
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
