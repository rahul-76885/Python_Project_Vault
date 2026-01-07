from market import app,db
from flask import render_template ,redirect , url_for,flash
from market.model import Item,User
from market.form import RegisterForm


# -------------------------------------------------
# HOME PAGE ROUTE
# -------------------------------------------------
# This route handles:
#   URL: /
#   URL: /home
#
# Both URLs point to the same function.
# Flask allows multiple routes for one view.
# -------------------------------------------------
@app.route('/')
@app.route('/home')
def home_page():
    # Renders the home.html template
    # No data is passed here
    return render_template('home.html')


# -------------------------------------------------
# MARKET PAGE ROUTE
# -------------------------------------------------
# This route displays all items available
# in the database.
# -------------------------------------------------
@app.route('/market')
def market_page():

    # Query the database to fetch ALL Item records
    # Item.query.all() returns a list of Item objects
    items = Item.query.all()

    # Pass the items list to the market.html template
    # so it can be displayed using a loop
    return render_template('market.html', items=items)


# -------------------------------------------------
# REGISTER PAGE ROUTE
# -------------------------------------------------
# This route:
# - Creates a RegisterForm instance
# - Sends it to the register.html template
#
# Currently, this route only handles GET requests.
# Form submission (POST) will be added later.
# -------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    # Create an instance of the registration form
    form = RegisterForm()

    # -------------------------------------------------
    # This block runs ONLY when:
    # - Request method is POST
    # - All form validations pass (NO errors)
    # -------------------------------------------------
    if form.validate_on_submit():
        
        # Create a new User object using form data
        user_to_create = User(
            name=form.username.data,
            email=form.email_address.data,
            password_hash=form.password1.data  # hashing usually handled in model
        )

        # Add the user to the database session
        db.session.add(user_to_create)

        # Commit changes to permanently save user in DB
        db.session.commit()

        # Success message shown on UI
        flash('Account created successfully!', category='success')

        # Redirect user to market page after successful registration
        return redirect(url_for('market_page'))

    # -------------------------------------------------
    # This block runs when:
    # - Form is submitted BUT validation FAILS
    # - Errors exist in form fields
    # -------------------------------------------------
    if form.errors:
        # form.errors is a dictionary:
        # { field_name: [error1, error2, ...] }
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, category='danger')

    # Render registration page and send form object to template
    return render_template('register.html', form=form)
