from market import app,db
from flask import render_template ,redirect , url_for
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
@app.route('/register' , methods=['GET','POST'])
def register_page():
   
    # Create an instance of the registration form
    form = RegisterForm()
     
    # here it is set of instruction used when i click on submit btn its stores data written in from in my user database
    if form.validate_on_submit():
        user_to_create = User(name=form.username.data,
                              email=form.email_address.data,
                              password_hash=form.password1.data)

        db.session.add(user_to_create)
        db.session.commit()
        if form.errors != {}: #If there are not errors from the validations
          for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')

        # Redirect to the market page after successful registration
        return redirect(url_for('market_page'))

    # Render the registration page and pass the form
    return render_template('register.html', form=form)
