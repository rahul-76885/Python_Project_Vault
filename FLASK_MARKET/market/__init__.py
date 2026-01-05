import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
# ensure the package's instance/ directory exists (market/instance)
os.makedirs(app.instance_path, exist_ok=True)

# store DB inside market/instance so Flask/SQLAlchemy use that path
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'market.db')}"
app.config['SECRET_KEY'] = 'dev'  # minimal secret for sessions/forms
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from market import routes
