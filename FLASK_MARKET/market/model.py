from market import db, bcrypt, login_manager
from flask_login import UserMixin


# -------------------------------------------------
# Flask-Login User Loader
# -------------------------------------------------
# Flask-Login stores only the user ID in the session.
# When a request comes, it calls this function
# to convert the stored user_id into a User object.
#
# Example:
# session["user_id"] = 7
# Flask-Login calls:
# load_user("7")
# and expects a User object in return.
# -------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# =========================
# USER MODEL
# =========================
class User(db.Model, UserMixin):
    """
    Represents a registered user.

    Inherits from:
    - db.Model → SQLAlchemy database model
    - UserMixin → Flask-Login helper methods
      (is_authenticated, get_id(), etc.)
    """

    # Primary key → unique identity for each user
    id = db.Column(db.Integer(), primary_key=True)

    # Username (must be unique and cannot be empty)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # Email address (unique, used for communication)
    email = db.Column(db.String(length=50), nullable=False, unique=True)

    # Stores only the HASHED password
    # Never store raw passwords in the database
    password_hash = db.Column(db.String(length=60), nullable=False)

    # Virtual money / wallet for the user
    budget = db.Column(db.Integer(), nullable=False, default=1000)

    # Relationship:
    # One User → Many Items
    # Allows:
    #   user.items  → all items owned by this user
    #   item.owned_user → the user who owns that item
    items = db.relationship('Item', backref='owned_user', lazy=True)

    # -------------------------------------------------
    # Password Getter
    # -------------------------------------------------
    # Allows:
    #   user.password
    # But returns the hashed password.
    # -------------------------------------------------
    @property
    def password(self):
        return self.password_hash

    # -------------------------------------------------
    # Password Setter
    # -------------------------------------------------
    # When we do:
    #   user.password = "mypassword"
    #
    # This function automatically:
    # - Hashes the password
    # - Stores it in password_hash
    # -------------------------------------------------
    @password.setter
    def password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(
            plain_password
        ).decode('utf-8')

    # -------------------------------------------------
    # Pretty formatted budget
    # Example:
    # 1000  → 1,000$
    # 500   → 500$
    # -------------------------------------------------
    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    # -------------------------------------------------
    # Password verification
    # Compares:
    # - hashed password in DB
    # - password typed by the user
    # -------------------------------------------------
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(
            self.password_hash,
            attempted_password
        )


# =========================
# ITEM MODEL
# =========================
class Item(db.Model):
    """
    Represents an item in the market.
    Each item can be owned by one user.
    """

    # Primary key
    id = db.Column(db.Integer(), primary_key=True)

    # Item name (must be unique)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # Price of the item
    price = db.Column(db.Integer(), nullable=False)

    # Unique product barcode
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)

    # Item description
    description = db.Column(db.String(length=1024), nullable=False, unique=True)

    # -------------------------------------------------
    # Foreign Key
    # Stores the ID of the User who owns this item
    #
    # user.id → Item.owner
    # -------------------------------------------------
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    # -------------------------------------------------
    # How the object appears when printed
    # -------------------------------------------------
    def __repr__(self):
        return f'Item {self.name}'

# 🔐 SECURE AUTHENTICATION FLOW (Flask-Login)

# USER ENTERS:
# Username + Password
#         │
#         ▼
# Browser sends POST /login
#         │
#         ▼
# Flask login_page()
#         │
#         ▼
# User.query.filter_by(username)
#         │
#         ▼
# bcrypt.check_password_hash()
#         │
#         ▼
# Password correct?
#    ┌───────────────┐
#    │ NO            │ → Reject login
#    └───────────────┘
#         │ YES
#         ▼
# login_user(user)
#         │
#         ▼
# UserMixin.get_id()
#         │
#         ▼
# user.id → "7"
#         │
#         ▼
# Flask creates:
# session["_user_id"] = "7"
#         │
#         ▼
# Flask signs session with SECRET_KEY
#         │
#         ▼
# Signed session cookie sent to browser
#         │
#         ▼
# USER IS NOW LOGGED IN


# 🔄 EVERY FUTURE REQUEST
# Browser sends request
#         │
#         │  (cookie auto-attached)
#         ▼
# Flask receives:
# session cookie
#         │
#         ▼
# Flask verifies signature using SECRET_KEY
#         │
#         ▼
# session["_user_id"] = "7"
#         │
#         ▼
# Flask-Login calls:
# load_user("7")
#         │
#         ▼
# User.query.get(7)
#         │
#         ▼
# current_user = User( Rahul, email, budget, items )
#         │
#         ▼
# Request continues as authenticated\


# How Flask-Login uses cookies and SECRET_KEY

# When a user logs in using login_user(user), Flask-Login does not store the user’s full data
# in the browser. It stores only the user’s ID in Flask’s session. This session data is then
# cryptographically signed using the application’s SECRET_KEY and sent to the browser as a
# session cookie. The browser simply stores this cookie and sends it back on every request.
# Flask uses the same SECRET_KEY to verify the signature of the cookie and ensure that it was
# created by the server and has not been modified. Because of this, even though the cookie is 
# stored in the browser, it cannot be trusted unless its signature is valid.


# What happens if someone tampers with the cookie in the browser

# A user or attacker can technically edit cookies in their own browser, for example trying to
#  change _user_id from 7 to 1 to impersonate another user. However, because the cookie is
#  signed with the server’s SECRET_KEY, any modification breaks the signature. When Flask
#  receives such a tampered cookie, it detects the invalid signature and rejects it, treating
#  the user as logged out. The server never loads another user from the database, and no data
#  is exposed. This ensures that even though cookies are stored on the client, all security
#  decisions are enforced on the server.