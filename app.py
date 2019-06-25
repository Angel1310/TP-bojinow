from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import UserMixin
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
bc = Bcrypt(app)
lm = LoginManager(app)
lm.login_view = 'login'
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=True)

    def __int__(self, username, password):
        self.username = username
        self.password = password
'''
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=True, unique=True)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, title, year):
        self.title = title
        self.year = year

class FilmSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'year')
''''
class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')
'''
film_schema = FilmSchema(strict=True)
films_schema = FilmSchema(many=True, strict=True)
'''
@app.route("/")
def home():
    return '<button><a action="POST" href="/film">POST</a></button>'

@app.route("/register", methods=['POST'])
def register(username, password):

    if request.methods == POST:
        new_user = User(username, password)

        db.session.add(new_user)
        db.session.commit()

    return reg

@app.route("/login", methods=['GET'])
def login(username, password):
    user = User.query.get(username)

    if user.password == password:
        return True

    return False
'''

@app.route("/film", methods=['POST'])
def add_film():
    title = request.json['title']
    year = request.json['year']

    if title is None or year is None:
        return abort(400)

    new_film = Film(title, year)

    db.session.add(new_film)
    db.session.commit()

    return film_schema.jsonify(new_film), 201

@app.route("/film", methods=['GET'])
def all_films():
    all_films = Film.query.all()
    result = films_schema.dump(all_films)
    return jsonify(result.data), 200

@app.route("/film/<int:film_id>", methods=['GET'])
def show_film(film_id):
    film = Film.query.get(film_id)
    if film is None:
        return abort(404)
    return film_schema.jsonify(film), 200

@app.route("/film/<int:film_id>", methods=['PUT'])
def edit_film(film_id):
    film = Film.query.get(film_id)
    if film is None:
        return abort(404)

    title = request.json['title']
    year = request.json['year']

    film.title = title
    film.year = year
    if title is None or year is None:
        return abort(400)

    db.session.commit(), 200

    return film_schema.jsonify(film)

@app.route("/film/<int:film_id>", methods=['DELETE'])
def remove_film(film_id):
    film = Film.query.get(film_id)
    if film is None:
        return abort(404)

    db.session.delete(film)
    db.session.commit()

    return film_schema.jsonify(film), 200     

if __name__ == '__main__':
    app.run(debug=True)