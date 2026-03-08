from blog import app, templates
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .schemas import POSTCREATE, POSTRESPONSE

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

posts = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]


# ---------------------------------------------------------------------------
# HTML routes
# ---------------------------------------------------------------------------
#
# include_in_schema=False
#   FastAPI auto-documents every route in /docs and /redoc by default.
#   HTML pages don't belong in API docs — this hides them.
#   Flask has no equivalent because it has no built-in API docs.
#
# name="home"
#   Gives the route a stable identifier, independent of the function name.
#   You can rename the function freely without breaking anything.
#   Used in templates as: {{ request.url_for('home') }} → "/"
#   Also prevents name collisions when using APIRouter across multiple files.
#
# request: Request  (dependency injection)
#   FastAPI explicitly injects the HTTP request object into the function.
#   Gives access to: request.headers, request.cookies,
#                    request.query_params, request.url, request.url.path
#   Flask uses a global proxy (from flask import request) — invisible, magical.
#   FastAPI makes it explicit — visible, testable, and mockable.
#
# templates.TemplateResponse()
#   FastAPI's equivalent of Flask's render_template().
#   Flask:   return render_template("home.html", posts=posts)  ← no request needed
#   FastAPI: must pass "request" explicitly — no global app context like Flask.
#
# "request": request  (required in every TemplateResponse)
#   Jinja2 needs it to run url_for() inside templates.
#   Used in HTML as:
#     {{ request.url_for('static', path='style.css') }} → /static/style.css
#     {{ request.url_for('home') }}                     → /
#   Forgetting this raises an error immediately (better than silent failure).

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def posts_page(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,   # required — Jinja2 needs it for url_for()
        "posts": posts,       # accessed in template as: {% for post in posts %}
        "title": "All Posts", # accessed in template as: {{ title }}
    })


@app.get("/posts/{post_id}", include_in_schema=False, name="post")
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse("post.html", {
                "request": request,
                "post": post,
            })
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# ---------------------------------------------------------------------------
# Static files — how the full sequence works
# ---------------------------------------------------------------------------
#
#  1. Server renders template:
#       Jinja2 replaces {{ request.url_for('static', path='style.css') }}
#       with the actual URL → /static/style.css
#       Browser receives plain HTML — it never sees Jinja syntax.
#
#  2. Browser reads the HTML:
#       Spots resource links (/static/style.css, /static/logo.png)
#       Fires a separate HTTP GET request for each resource.
#
#  3. FastAPI serves the files:
#       app.mount("/static", StaticFiles(directory="static"), name="static")
#       Maps: GET /static/style.css → file: static/style.css on disk.
#       Returned directly — your Python route functions are never called.
#
#  One-line: url_for() builds URL → Jinja writes it into HTML
#            → browser requests it → app.mount() serves the file directly.


# ---------------------------------------------------------------------------
# JSON API routes  (visible in /docs — that's the point for API routes)
# ---------------------------------------------------------------------------
#
# FastAPI auto-converts returned dicts/lists to JSON — no jsonify() needed.
#
# post_id: int  (automatic validation)
#   FastAPI reads the path param as a string, then coerces it to int.
#   If the user sends /api/posts/abc → RequestValidationError is raised
#   automatically before your code even runs.
#   Flask would pass "abc" through silently and crash inside your logic.

# GET all posts
# This endpoint handles HTTP GET requests to /api/posts
# response_model tells FastAPI what structure the response should follow
# list[POSTRESPONSE] means the API will return a list of PostResponse objects
@app.get("/api/posts", response_model=list[POSTRESPONSE])
async def get_posts():
    # posts is a Python list containing dictionaries
    # FastAPI automatically converts Python list/dict → JSON response
    return posts


# POST endpoint to create a new post
# response_model=POSTRESPONSE means the returned data must match this schema
# status_code=201 means "resource created successfully"
@app.post(
    "/api/posts",
    response_model=POSTRESPONSE,
    status_code=status.HTTP_201_CREATED
)
def post_create(post: POSTCREATE):

    # Generate a new id for the post
    # If posts exist → find the highest id and add 1
    # If list is empty → start id from 1
    new_id = max(p["id"] for p in posts) + 1 if posts else 1

    # Create a new post dictionary
    # post.author, post.title, post.content come from the POST request body
    # POSTCREATE schema already validated this data
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }

    # Add the new post to our posts list (temporary storage)
    # In real applications this would be saved in a database
    posts.append(new_post)

    # Return the created post
    # FastAPI validates it against POSTRESPONSE schema
    return new_post


# GET endpoint to retrieve a single post by its id
# {post_id} is a path parameter
# Example request: /api/posts/2
@app.get("/api/posts/{post_id}", response_model=POSTRESPONSE)
async def get_post(post_id: int):

    # Loop through all posts to find the matching id
    for post in posts:

        # .get() safely retrieves the "id" key
        # returns None if key does not exist instead of crashing
        if post.get("id") == post_id:
            # If post found → return it
            # FastAPI converts dict → JSON automatically
            return post

    # If loop finishes and no post was found
    # raise HTTPException to send a proper API error response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,  # HTTP status code
        detail="not found"  # message returned in response body
    )

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
#
# Both handlers apply the same routing rule:
#   request path starts with /api  →  return JSON  (API clients expect JSON)
#   everything else                →  return HTML  (browsers expect a page)
#
# Why StarletteHTTPException instead of FastAPI's HTTPException?
#   FastAPI's HTTPException inherits from StarletteHTTPException.
#   Registering the handler on the parent class catches both — one handler
#   covers all HTTP errors (404, 403, 405, etc.) regardless of where they
#   were raised (your code or FastAPI internals).

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = exception.detail or "An error occurred. Please check your request and try again."

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,  # actual HTTP status sent to client
            content={"detail": message},        # JSON body
        )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exception.status_code,  # used inside the HTML template
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,  # actual HTTP response status
    )


# Triggered when a path or query param fails type validation.
# Example: GET /api/posts/abc  →  post_id expects int  →  422 raised here.
# exception.errors() returns a structured list describing what failed and why.
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()},  # structured list of validation failures
        )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# ---------------------------------------------------------------------------
# Full request lifecycle
# ---------------------------------------------------------------------------
#
#  Browser / API client
#       │
#       │  HTTP Request
#       ▼
#  ┌─────────────────────────────────────────────────────┐
#  │  FastAPI router                                     │
#  │  matches URL path + HTTP method to a route function │
#  └─────────────────────────────────────────────────────┘
#       │
#       ▼
#  ┌─────────────────────────────────────────────────────┐
#  │  Dependency injection  (automatic)                  │
#  │  request: Request — HTTP request object injected    │
#  │  post_id: int     — path param extracted + coerced  │
#  │  invalid type (e.g. "abc") → RequestValidationError │
#  └─────────────────────────────────────────────────────┘
#       │                              │
#       │ valid params                 │ invalid params
#       ▼                              ▼
#  Route function runs        validation_exception_handler
#       │                              │
#       │                           /api/* ?
#       │                          ┌────┴────┐
#       │                        JSON       HTML
#       │                     {"detail":…} error.html (422)
#       │
#       ├─ return dict / list
#       │    FastAPI serializes → JSON response automatically
#       │
#       ├─ return TemplateResponse
#       │    Jinja2 renders → HTML response sent to browser
#       │
#       └─ raise HTTPException(status_code=..., detail=...)
#                │
#                ▼
#         http_exception_handler
#         (StarletteHTTPException catches FastAPI's too)
#                │
#             /api/* ?
#            ┌────┴────┐
#          JSON       HTML
#       {"detail":…} error.html (status_code)
#
#
# ---------------------------------------------------------------------------
# Static file request lifecycle (separate flow — never hits route functions)
# ---------------------------------------------------------------------------
#
#  Browser requests /static/style.css
#       │
#       ▼
#  app.mount("/static", StaticFiles(directory="static"), name="static")
#       │
#       ▼
#  File read from disk and returned directly to browser
#  (no route function, no Jinja2, no exception handlers involved)