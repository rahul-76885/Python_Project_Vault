from market import db, bcrypt, login_manager
from flask_login import UserMixin


# =================================================
# FLASK-LOGIN USER LOADER
# =================================================
# Core idea:
# Flask-Login NEVER stores the full User object in the session.
# It stores ONLY a STRING user_id.
#
# Common confusion:
# ❌ "Is the User object stored in cookies?"
# ✅ No. Only user_id is stored; User object is reconstructed per request.
#
# Lifecycle:
# - Runs ON EVERY REQUEST where session contains a user_id
# - Converts user_id → User ORM object
#
# IMPORTANT:
# This function MUST:
# - Return a User object
# - Or return None (treated as anonymous user)
# =================================================
@login_manager.user_loader
def load_user(user_id):
    # user_id arrives as STRING because sessions store JSON-serializable data
    # Conversion to int is REQUIRED for primary key lookup
    #
    # User.query.get():
    # - Uses primary key
    # - Returns None if not found
    # - Does NOT raise exception
    return User.query.get(int(user_id))


# =================================================
# USER MODEL
# =================================================
class User(db.Model, UserMixin):
    """
    Represents a registered user.

    Architectural role:
    - Owns authentication rules
    - Owns password logic
    - Owns relationships

    Routes SHOULD NOT:
    - Hash passwords
    - Compare passwords
    - Know storage details
    """

    # -------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------
    # Acts as:
    # - Database identity
    # - Authentication identity
    # - Foreign key reference target
    id = db.Column(db.Integer(), primary_key=True)

    # -------------------------------------------------
    # USERNAME
    # -------------------------------------------------
    # unique=True:
    # ✔ Prevents duplicates at DB level
    # ✘ Validation alone is NOT sufficient (race conditions)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------
    # Stored as plain text because:
    # - Needed for communication
    # - Not secret like passwords
    email = db.Column(db.String(length=50), nullable=False, unique=True)

    # -------------------------------------------------
    # PASSWORD HASH
    # -------------------------------------------------
    # Stores ONLY hash
    #
    # NEVER:
    # - Store raw password
    # - Return raw password
    password_hash = db.Column(db.String(length=60), nullable=False)

    # -------------------------------------------------
    # BUDGET
    # -------------------------------------------------
    # Default assigned at DB level
    # Ensures consistency even if object is created outside routes
    budget = db.Column(db.Integer(), nullable=False, default=1000)

    # -------------------------------------------------
    # RELATIONSHIP: USER → ITEMS
    # -------------------------------------------------
    # lazy=True means:
    # - Items are fetched only when accessed
    #
    # Common confusion:
    # ❌ "Is user.items always loaded?"
    # ✅ No. It triggers a query when accessed.
    items = db.relationship('Item', backref='owned_user', lazy=True)

    # =================================================
    # PASSWORD PROPERTY (READ)
    # =================================================
    @property
    def password(self):
        # Returning hash prevents accidental plaintext exposure
        #
        # Design choice:
        # ❌ Do not allow reading real password
        return self.password_hash

    # =================================================
    # PASSWORD PROPERTY (WRITE)
    # =================================================
    @password.setter
    def password(self, plain_password):
        # Hashing happens HERE to:
        # ✔ Centralize security logic
        # ✔ Make routes ignorant of hashing algorithm
        #
        # If algorithm changes later (bcrypt → argon2),
        # routes remain untouched.
        self.password_hash = bcrypt.generate_password_hash(
            plain_password
        ).decode('utf-8')

    # =================================================
    # DERIVED PROPERTY (NOT STORED IN DB)
    # =================================================
    @property
    def prettier_budget(self):
        # Computed property:
        # - Exists only in Python
        # - NOT stored in database
        #
        # Common confusion:
        # ❌ "Is this column in DB?"
        # ✅ No. It is derived at runtime.
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    # =================================================
    # PASSWORD VERIFICATION
    # =================================================
    def check_password_correction(self, attempted_password):
        # bcrypt.check_password_hash():
        # - Handles salting internally
        # - Safe against timing attacks
        #
        # try/except rationale:
        # If DB hash is corrupted or invalid,
        # treat as failed login instead of crashing server.
        try:
            return bcrypt.check_password_hash(
                self.password_hash,
                attempted_password
            )
        except ValueError:
            return False


# =================================================
# ITEM MODEL
# =================================================
class Item(db.Model):
    """
    Represents a market item.

    Data ownership:
    - Item knows WHO owns it
    - User knows WHICH items they own
    """

    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(length=30), nullable=False, unique=True)

    price = db.Column(db.Integer(), nullable=False)

    barcode = db.Column(db.String(length=12), nullable=False, unique=True)

    description = db.Column(db.String(length=1024), nullable=False, unique=True)

    # -------------------------------------------------
    # FOREIGN KEY
    # -------------------------------------------------
    # owner stores ONLY user.id
    #
    # Relationship resolution:
    # Item.owner        → integer
    # Item.owned_user   → User object (via backref)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        # Developer-facing representation
        # Used in debugging, logs, shell
        return f'Item {self.name}'


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