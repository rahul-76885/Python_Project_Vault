from flask import Flask, render_template  # Import Flask class and template rendering utility

# Create an instance of the Flask application
# __name__ helps Flask determine the root directory of this file,
# which is necessary to correctly locate templates and static assets
app = Flask(__name__)

# ---------------- HOME ROUTES ----------------
# Multiple routes can point to the same function
# Both '/' and '/home' will render the same template
@app.route('/')
@app.route('/home')
def home_page():
    # Renders the home.html file from the templates/ directory
    return render_template("home.html")

# ---------------- MARKET ROUTE ----------------
# Route for the market page
# This route prepares data in Python and sends it to the template
@app.route('/market')
def market_page():
    # List of items (simulating data from a database)
    items = [
        {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
        {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
        {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    ]

    # Pass the items list to market.html using Jinja templating
    return render_template('market.html', items=items)
