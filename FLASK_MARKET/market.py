from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# -------------------------------------------------
# Create the Flask application instance
# __name__ tells Flask where this file is located,
# so it can correctly resolve paths (templates, static, database)
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# DATABASE CONFIGURATION
# -------------------------------------------------

# if we want to connect database to flask we can't do it directly so we use SQLALCHEMY(python library)

# Flask app
#    ↓ provides config
# SQLAlchemy
#    ↓ connects using URI
# SQLite database

# SQLALCHEMY_DATABASE_URI tells SQLAlchemy:
# 1. Which database engine to use (sqlite)
# 2. Where the database file is located

# 'sqlite:///market.db' means:
# sqlite   -> database engine
# ///      -> current project directory
# market.db -> database file name

# This will create market.db automatically if it does not exist
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

# (Optional but recommended)
# Disables a feature that tracks object changes
# It saves memory and avoids warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------------------------------------
# INITIALIZE SQLALCHEMY
# -------------------------------------------------

# We pass the Flask app to SQLAlchemy so it knows:
# - which app configuration to use
# - which database URI to connect to
# - where the application context is
db = SQLAlchemy(app)

# -------------------------------------------------
# DATABASE MODEL (TABLE / Outside the file)
# -------------------------------------------------

# we will create a python class that represents a TABLE in the database
# Item -> item table
# Each class attribute -> column in the table
#
# db.Model is the BASE ORM class provided by SQLAlchemy
# By inheriting from it, SQLAlchemy knows this is a database model
class Item(db.Model):

    # Primary key column
    # Automatically increments (1, 2, 3, ...)
    id = db.Column(db.Integer, primary_key=True)

    # String column with max length 20
    # nullable=False -> value cannot be empty
    # unique=True -> no duplicate names allowed
    name = db.Column(db.String(length=20), nullable=False, unique=True)

    # Integer column for price
    price = db.Column(db.Integer, nullable=False)

    # Barcode must be unique for each item
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)

    # Description of the item
    description = db.Column(db.String(length=100), nullable=False)

    # This method is OPTIONAL but very helpful
    # It defines how an object is printed when debugging
    def __repr__(self):
        return f"Item('{self.name}', '{self.price}')"

#Commands i ran in flask Shell
# from market import db
# db.create_all()
# from market import Items
# item1=Items(name="rahul",price=100,barcode="1288282",description="this is a first database")
# db.session.add(item1)
# db.session.commit()

#Item.query.all()
# for item in Item.query.all():
    # item.name
    # item.price
    # item.description
# for item in Item.query.filter_by(price=500):
    # item.name
    # item.price
    # item.description

# ---------------- HOME ROUTES ----------------
# Multiple routes can point to the same function
# Both '/' and '/home' will render the same template
@app.route('/')
@app.route('/home')
def home_page():
    # Renders the home.html file from the templates/ directory
    return render_template("home.html")


# # -------------------------------------------------
# # DATABASE (Inside the file)
# # -------------------------------------------------
# # Route for the market page
# # This route prepares data in Python and sends it to the template
# # As our data grows we need a seperate folder to store it so our code look clean 
# @app.route('/market')
# def market_page():
#     # List of items (simulating data from a database)
#     items = [
#         {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
#         {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
#         {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
#     ]

#     # Pass the items list to market.html using Jinja templating
#     return render_template('market.html', items=items)



@app.route('/market')
def market_page():
    # List of items (simulating data from a database)
    items=Item.query.all()
    # Pass the items list to market.html using Jinja templating
    return render_template('market.html', items=items)



