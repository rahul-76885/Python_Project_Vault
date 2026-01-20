# ------------------ IMPORTS ------------------
# Flask: core web framework (handles HTTP requests)
from flask import Flask

# Flask-RESTful: adds REST abstractions on top of Flask
# Resource → maps HTTP methods to class methods
# reqparse → validates incoming request data
# abort → stops request and returns HTTP error
# fields + marshal_with → serialize objects into JSON
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

# SQLAlchemy: ORM to talk to database using Python objects
from flask_sqlalchemy import SQLAlchemy


# ------------------ APP & API SETUP ------------------

# Create Flask application instance
app = Flask(__name__)

# Wrap Flask with Flask-RESTful
# Api object intercepts requests and routes them to Resource classes
api = Api(app)

# Configure database connection (SQLite file)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize SQLAlchemy with Flask app
# db now manages DB connections, sessions, and models
db = SQLAlchemy(app)


# ------------------ DATABASE MODEL ------------------

# VideoModel represents ONE ROW in the "video_model" table
# ORM = Object Relational Mapping
# Python object ↔ Database row
class VideoModel(db.Model):

    # Primary key column
    id = db.Column(db.Integer, primary_key=True)

    # Non-nullable string column
    name = db.Column(db.String(100), nullable=False)

    # Non-nullable integer columns
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    # Used only for debugging (not sent to client)
    def __repr__(self):
        return f"Video(name={self.name}, views={self.views}, likes={self.likes})"


# ------------------ REQUEST PARSERS ------------------

# reqparse defines WHAT INPUT the API accepts

# PUT parser → all fields required (full object creation)
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, required=True)
video_put_args.add_argument("views", type=int, required=True)
video_put_args.add_argument("likes", type=int, required=True)

# PATCH parser → all fields optional (partial update)
video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str)
video_update_args.add_argument("views", type=int)
video_update_args.add_argument("likes", type=int)


# ------------------ RESPONSE SERIALIZATION ------------------

# resource_fields tells Flask-RESTful:
# "When returning a VideoModel object, expose ONLY these fields"
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}


# ------------------ RESOURCE CLASS ------------------

# Resource = a REST endpoint
# One Resource class = one URL pattern
class Video(Resource):

    # GET /video/<id>
    @marshal_with(resource_fields)
    def get(self, video_id):

        # Query database for video
        result = VideoModel.query.filter_by(id=video_id).first()

        # If not found → stop request & return 404
        if not result:
            abort(404, message="Could not find video with that id")

        # Return Python object
        # Flask-RESTful handles conversion → JSON → HTTP response
        return result


    # PUT /video/<id>
    @marshal_with(resource_fields)
    def put(self, video_id):

        # Parse & validate JSON body
        args = video_put_args.parse_args()

        # Prevent duplicate ID
        if VideoModel.query.filter_by(id=video_id).first():
            abort(409, message="Video id already exists")

        # Create Python ORM object
        video = VideoModel(
            id=video_id,
            name=args['name'],
            views=args['views'],
            likes=args['likes']
        )

        # Stage object for DB insert
        db.session.add(video)

        # Commit transaction (writes to DB)
        db.session.commit()

        # Return object (serialized automatically)
        return video, 201


    # PATCH /video/<id>
    @marshal_with(resource_fields)
    def patch(self, video_id):

        # Parse optional fields
        args = video_update_args.parse_args()

        # Fetch existing row
        result = VideoModel.query.filter_by(id=video_id).first()

        if not result:
            abort(404, message="Video doesn't exist")

        # Update ONLY provided fields
        if args['name'] is not None:
            result.name = args['name']
        if args['views'] is not None:
            result.views = args['views']
        if args['likes'] is not None:
            result.likes = args['likes']

        # Save changes
        db.session.commit()

        return result


    # DELETE /video/<id>
    def delete(self, video_id):

        # Fetch row
        result = VideoModel.query.filter_by(id=video_id).first()

        if not result:
            abort(404, message="Video doesn't exist")

        # Delete row
        db.session.delete(result)
        db.session.commit()

        return '', 204


# ------------------ ROUTE REGISTRATION ------------------

# Connect URL → Resource class
# Flask-RESTful maps HTTP methods automatically
api.add_resource(Video, "/video/<int:video_id>")


# ------------------ DATABASE INITIALIZATION ------------------

# Create tables ONCE
with app.app_context():
    db.create_all()


# ------------------ RUN SERVER ------------------

if __name__ == "__main__":
    app.run(debug=True)
