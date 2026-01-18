from market import db, bcrypt, login_manager
from flask_login import UserMixin, current_user


# =================================================
# WHAT DOES `from flask_login import current_user` MEAN?
# =================================================
# INTERVIEW QUESTION:
# Q: When we import `current_user`, what do we actually get?
#
# ANSWER:
# `current_user` is NOT a User object.
# It is a PROXY (lazy object).
#
# Meaning:
# - It does NOT store a user permanently
# - It dynamically resolves to:
#   → the User for THIS request
#
# On every request:
# current_user → load_user(user_id) → User object
#
# If user is not logged in:
# current_user → AnonymousUser
#
# IMPORTANT:
# You NEVER manually pass user.id.
# Flask-Login reconstructs the user automatically.
# =================================================


# =================================================
# FLASK-LOGIN USER LOADER
# =================================================
# INTERVIEW QUESTION:
# Q: How does Flask-Login know which user is logged in?
#
# ANSWER:
# - Flask-Login stores ONLY user_id in the session
# - On every request it calls this function
# - This function rebuilds the User object
# =================================================
@login_manager.user_loader
def load_user(user_id):
    # user_id comes as STRING from session cookie
    # Convert to int for DB primary key lookup
    return User.query.get(int(user_id))



# =================================================
# USER MODEL (AUTH + DOMAIN LOGIC)
# =================================================
class User(db.Model, UserMixin):
    """
    Represents a registered user.

    INTERVIEW QUESTION:
    Q: Why inherit UserMixin?
    A: It provides is_authenticated, get_id(), etc.,
       which Flask-Login requires to function.

    DESIGN PRINCIPLE:
    - Routes orchestrate
    - Models enforce business & security rules
    """

    # -------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------
    # INTERVIEW QUESTION:
    # Q: Why is id important beyond DB identity?
    # A: It is also used for authentication and relationships.
    id = db.Column(db.Integer(), primary_key=True)

    # -------------------------------------------------
    # USERNAME
    # -------------------------------------------------
    # unique=True:
    # ✔ DB-level protection
    # ✘ Forms alone are not enough (race conditions)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------
    # Stored as plaintext because it is NOT secret.
    email = db.Column(db.String(length=50), nullable=False, unique=True)

    # -------------------------------------------------
    # PASSWORD HASH
    # -------------------------------------------------
    # INTERVIEW QUESTION:
    # Q: Why never store plaintext passwords?
    # A: DB leaks would expose user credentials.
    password_hash = db.Column(db.String(length=60), nullable=False)

    # -------------------------------------------------
    # BUDGET
    # -------------------------------------------------
    # Default enforced at DB level for consistency.
    budget = db.Column(db.Integer(), nullable=False, default=1000)

    # -------------------------------------------------
    # RELATIONSHIP: USER → ITEMS
    # -------------------------------------------------
    # lazy=True → query executed ONLY when accessed
    items = db.relationship('Item', backref='owned_user', lazy=True)

    # =================================================
    # PASSWORD PROPERTY (READ)
    # =================================================
    @property
    def password(self):
        # INTERVIEW QUESTION:
        # Q: Why not return the real password?
        # A: Passwords should NEVER be readable.
        return self.password_hash

    # =================================================
    # PASSWORD PROPERTY (WRITE)
    # =================================================
    @password.setter
    def password(self, plain_password):
        # WHY HASHING IS HERE:
        # - Centralizes security logic
        # - Keeps routes clean
        # - Allows algorithm change without touching routes
        self.password_hash = bcrypt.generate_password_hash(
            plain_password
        ).decode('utf-8')

    # =================================================
    # DERIVED PROPERTY (NOT STORED IN DB)
    # =================================================
    @property
    def prettier_budget(self):
        # INTERVIEW QUESTION:
        # Q: Is this a database column?
        # A: No. It is computed at runtime.
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        return f"{self.budget}$"

    # =================================================
    # PASSWORD VERIFICATION
    # =================================================
    def check_password_correction(self, attempted_password):
        # INTERVIEW QUESTION:
        # Q: Why compare hashes instead of passwords?
        # A: Passwords are never stored or compared directly.
        try:
            return bcrypt.check_password_hash(
                self.password_hash,
                attempted_password
            )
        except ValueError:
            # Defensive programming: corrupted hash
            return False

    # =================================================
    # AUTHORIZATION LOGIC
    # =================================================
    def can_purchase(self, item_obj):
        # INTERVIEW QUESTION:
        # Q: Why is this method on User?
        # A: Budget belongs to User, so permission logic belongs here.
        return self.budget >= item_obj.price
    def can_sell(self, item_obj):
        return item_obj in self.items

# =================================================
# ITEM MODEL (OWNERSHIP + TRANSACTION LOGIC)
# =================================================
class Item(db.Model):
    """
    Represents a market item.

    DESIGN PRINCIPLE:
    - Item owns ownership changes
    - User owns permission logic
    """

    id = db.Column(db.Integer(), primary_key=True)

    # Human-readable, NOT identity
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    price = db.Column(db.Integer(), nullable=False)

    barcode = db.Column(db.String(length=12), nullable=False, unique=True)

    description = db.Column(db.String(length=1024), nullable=False, unique=True)

    # -------------------------------------------------
    # FOREIGN KEY
    # -------------------------------------------------
    # Stores ONLY user.id (never full object)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user):
        # INTERVIEW QUESTION:
        # Q: Why is buy() inside Item and not User?
        # A: Ownership changes on Item, so behavior belongs here.
        self.owner = user.id
        user.budget -= self.price

        # NOTE:
        # In production, commit should be in route/service layer
        db.session.commit()
    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()
# =================================================
# AUTHENTICATION FLOW — RESEARCH SUMMARY
# =================================================
#
# KEY PRINCIPLES:
# 1. Session stores identifiers, NOT objects
# 2. ORM objects are recreated per request
# 3. Cookies are client-stored but server-trusted only if signed
# 4. SECRET_KEY is the root of trust
#
# If SECRET_KEY changes:
# - ALL existing sessions become invalid
#
# Security mental model:
# Client can SEE cookies
# Client CANNOT forge cookies
# Server ALWAYS re-verifies identity


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