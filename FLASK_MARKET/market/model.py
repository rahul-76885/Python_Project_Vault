from market import db
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# USER MODEL
# =========================
class User(db.Model):
    # Primary key → unique identity for each user
    id = db.Column(db.Integer(), primary_key=True)

    # Username (must be unique and cannot be empty)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # Email (unique identifier for login / communication)
    email = db.Column(db.String(length=50), nullable=False, unique=True)

    # Stores HASHED password, NOT the real password
    # Hashing makes passwords unreadable and secure
    password_hash = db.Column(db.String(length=60), nullable=False)

    # User wallet / budget (default value if not provided)
    budget = db.Column(db.Integer(), nullable=False, default=1000)

    # Relationship: One User → Many Items
    # This allows: user.items → list of items owned by user
    # backref creates reverse access: item.owned_user → user object
    # lazy=True means items are loaded only when accessed
    items = db.relationship('Item', backref='owned_user', lazy=True)

    # Converts plain password into a secure hash
    # This method is called while creating or updating a user
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


# =========================
# ITEM MODEL
# =========================
class Item(db.Model):
    # Primary key → unique identity for each item
    id = db.Column(db.Integer(), primary_key=True)

    # Item name (unique and required)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # Price of the item
    price = db.Column(db.Integer(), nullable=False)

    # Unique product barcode
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)

    # Item description
    description = db.Column(db.String(length=1024), nullable=False, unique=True)

    # Foreign Key:
    # Stores the id of the user who owns this item
    # Links Item → User using user.id
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    # String representation (useful for debugging & shell)
    def __repr__(self):
        return f'Item {self.name}'
