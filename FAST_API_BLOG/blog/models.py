# models.py — Defines database structure. Each class = one table, each variable = one column.
# SQLAlchemy reads this and creates actual tables in the database.

from sqlalchemy import String, Text, ForeignKey, Integer, DateTime  # column data types
from sqlalchemy.orm import mapped_column, Mapped, relationship       # FIX: 'relationship' not 'Relationship'
from datetime import datetime, UTC                                   # FIX: was missing this import
from database import Base                                            # parent class — connects models to DB


class User(Base):
    # __tablename__ — actual SQL table name. Python uses 'User', SQL uses 'users'
    __tablename__ = "users"

    # PRIMARY KEY — unique ID per row. index=True makes search faster.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # mapped_column() defines the column. String(50) = max length. nullable=False = required. unique=True = no duplicates.
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    # Optional column — user may not upload a photo. Stores filename only (e.g. "abc.jpg"), not full path.
    image_file: Mapped[str | None] = mapped_column(String(120), default=None, nullable=True)

    # RELATIONSHIP — Python-only link. Lets you do: user.posts → get all posts by this user.
    # FIX: was mapped_column(Relationship(...)) — relationship() is NOT a column, remove mapped_column()
    # FIX: "Post" in quotes because Post class is not defined yet at this point
    # ForeignKey = database link (stores user_id number) | relationship = Python access (gives full object)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

    # @property — computed value, NOT stored in DB. Access as user.image_path (no brackets).
    # Pydantic/FastAPI calls this automatically when converting User object to JSON response.
    # Why not store full path? If folder moves, all stored paths break. Filename is safer.
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"  # fallback if no photo uploaded


class Post(Base):
    # __tablename__ — actual SQL table name. Python uses 'Post', SQL uses 'posts'
    __tablename__ = "posts"

    # PRIMARY KEY — unique ID per post. index=True makes search faster.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(50), nullable=False)   # required
    content: Mapped[str] = mapped_column(Text, nullable=False)        # FIX: Text() not String(120) — 120 chars too short for post content

    # FOREIGN KEY — database-level link to users table. Stores user's id (e.g. 3), not the full user.
    # Ensures every post belongs to a valid user. index=True = fast lookup when fetching posts by user.
    # Relationship flow: user.id ←→ post.user_id | user.posts → all posts | post.author → user object
    # One-to-many: one user can have many posts.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Stores post creation time. lambda = runs fresh on each insert (without lambda, all posts get same timestamp).
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # RELATIONSHIP — Python-only link. Lets you do: post.author → get the full User object.
    author: Mapped["User"] = relationship(back_populates="posts")