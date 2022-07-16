# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    # genre = fields.Nested(GenreSchema, only=["name"])
    # director = fields.Nested(DirectorSchema, only=["name"])
    genre = fields.Pluck(GenreSchema, "name")
    director =fields.Pluck(DirectorSchema, "name")


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


@movies_ns.route("/")
class MoviesView(Resource):

    @movies_ns.param("director_id", "Director identification", "query")
    @movies_ns.param("genre_id", "Genre identification", "query")
    def get(self):

        query: Query = Movie.query

        director_id = request.args.get("director_id", None, type=int)
        genre_id = request.args.get("genre_id", None, type=int)

        if director_id:
            query: Query = query.filter(Movie.director_id == director_id)

        if genre_id:
            query: Query = query.filter(Movie.genre_id == genre_id)

        data = query.all()

        return movies_schema.dump(data), 200


@movies_ns.route("/<int:pk>")
class MovieView(Resource):

    def get(self, pk):
        movie = Movie.query.get(pk)
        return (movie_schema.dump(movie), 200) if movie is not None else ("Movie not found", 404)


@directors_ns.route("/")
class DirectorsView(Resource):

    def post(self):
        json_object = request.json
        director = Director(**json_object)
        try:
            with db.session():
                db.session.add(director)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

        return "Created", 201


@directors_ns.route("/<int:pk>")
class DirectorView(Resource):

    def put(self, pk):
        director: Director = Director.query.get(pk)
        if director is None:
            return "Director not found", 404
        json_object = request.json
        director.name = json_object.get("name")
        with db.session():
            db.session.add(director)
            db.session.commit()
        return "", 204

    def delete(self, pk):
        director: Director = Director.query.get(pk)
        if director is None:
            return "Director not found", 404
        with db.session():
            db.session.delete(director)
            db.session.commit()
        return "", 204


@genres_ns.route("/")
class GenresView(Resource):

    def post(self):
        json_object = request.json
        genre = Genre(**json_object)
        try:
            with db.session():
                db.session.add(genre)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

        return "Created", 201


@genres_ns.route("/<int:pk>")
class GenreView(Resource):

    def put(self, pk):
        genre: Genre = Genre.query.get(pk)
        if genre is None:
            return "Genre not found", 404
        json_object = request.json
        genre.name = json_object.get("name")
        with db.session():
            db.session.add(genre)
            db.session.commit()
        return "", 204

    def delete(self, pk):
        genre: Genre = Genre.query.get(pk)
        if genre is None:
            return "Genre not found", 404
        with db.session():
            db.session.delete(genre)
            db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
