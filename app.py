from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_login import UserMixin
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['SECRET_KEY'] = 'bf6423960e622d5907915c5292cab550'
db = SQLAlchemy(app)
ma = Marshmallow(app)
bc = Bcrypt(app)
lm = LoginManager(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

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

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

film_schema = FilmSchema(strict=True)
films_schema = FilmSchema(many=True, strict=True)

user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    if username is None or password is None:
        return abort(400)    
    
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return abort(400)
    

    hashed_pass = bc.generate_password_hash(password).decode('utf-8')
    new_user = User(username, hashed_pass)

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return user_schema.jsonify(new_user), 201

@app.route("/users", methods=['GET'])
def all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data), 200


@app.route("/login", methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if username is None or password is None:
        return abort(400)

    user = User.query.filter_by(username=username).first()
    if user is None:
        return abort(404)

    if not bc.check_password_hash(user.password, password):
        return abort(401)

    login_user(user)
    return user_schema.jsonify(user), 200

@app.route("/logout", methods=['GET'])
def logout():
    if not current_user:
        return abort(401)

    logout_user()
    return user_schema.jsonify(current_user), 200

@app.route("/user", methods=['GET'])
def cur_user():
    if not current_user:
        return abort(401)

    return user_schema.jsonify(current_user), 200

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