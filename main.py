from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import api_movie
import os
from dotenv import load_dotenv
import scraping
from urllib.parse import unquote

all_porn_stars = scraping.all_porn_stars()

load_dotenv()
DB_URI = os.getenv("DB_URI")
FLASK_KEY = os.getenv("FLASK_KEY")
IMG = os.getenv("IMG")
NIMG = "https://image.tmdb.org/t/p/originalNone"

app = Flask(__name__)
app.config['SECRET_KEY'] = f'{FLASK_KEY}'
app.config['SQLALCHEMY_DATABASE_URI'] = f'{DB_URI}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)
db.echo = True


class User(UserMixin, db.Model):
    __tablename__ = "users_saves"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)
    models = db.relationship("Model", backref="user", cascade="all, delete, save-update")
    tvs = db.relationship("Tv", backref="user", cascade="all, delete, save-update")
    actors = db.relationship("Actor", backref="user", cascade="all, delete, save-update")
    movies = db.relationship("Movie", backref="user", cascade="all, delete, save-update")


class Model(UserMixin, db.Model):
    __tablename__ = "models"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_saves.id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)


class Movie(UserMixin, db.Model):
    __tablename__ = "movies_saves"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_saves.id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)


class Tv(UserMixin, db.Model):
    __tablename__ = "tvs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_saves.id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)


class Actor(UserMixin, db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_saves.id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Search")


@app.route("/")
@login_required
def main():
    return redirect(url_for("discover", page=1, content="movie"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect("/")
        if not user:
            email = form.email.data
            password = form.password.data
            new_user = User(email=email, password=generate_password_hash(password, salt_length=8))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect("/")
    return render_template("login.html", form=form)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    """ Searching methods """
    if "s" in request.args:
        if request.args.get("s") == "movie":
            if request.method == "POST":
                movie_name = request.form.get("movie")
                if request.args.get("page"):
                    page = request.args.ge('page')
                    movie_data = api_movie.search_movies(movie_name, page)
                    return render_template("search.html", page=page, name=movie_name, s="movie", movie=movie_data,
                                           nimg=NIMG, img=IMG)
                else:
                    page = 1
                    movie_data = api_movie.search_movies(movie_name, page)
                    return render_template("search.html", page=page, name=movie_name, s="movie", movie=movie_data,
                                           nimg=NIMG, img=IMG)
            elif "name" and "page" in request.args:
                page = request.args.get("page")
                movie_name = request.args.get("name")
                movie_data = api_movie.search_movies(movie_name, page)
                return render_template("search.html", page=page, name=movie_name, s="movie", movie=movie_data,
                                       nimg=NIMG, img=IMG)

            return render_template("search.html", s="movie")
        elif request.args.get("s") == "series":
            if request.method == "POST":
                tv_name = request.form.get("movie")
                if "page" in request.args:
                    page = int(request.args.get("page"))
                    tv_data = api_movie.search_tv(tv_name, page)
                    return render_template("search.html", name=tv_name, page=page, s="series", tv=tv_data, nimg=NIMG,
                                           img=IMG)
                else:
                    page = 1
                    tv_data = api_movie.search_tv(tv_name, page)
                    return render_template("search.html", name=tv_name, page=page, s="series", tv=tv_data, nimg=NIMG,
                                           img=IMG)
            elif "page" and "name" in request.args:
                page = int(request.args.get("page"))
                tv_name = request.args.get("name")
                tv_data = api_movie.search_tv(tv_name, page)
                return render_template("search.html", name=tv_name, page=page, s="series", tv=tv_data, nimg=NIMG,
                                       img=IMG)

            return render_template("search.html", s="series")
        elif request.args.get("s") == "actors":
            if request.method == "POST":
                ppl_name = request.form.get("movie")
                if request.args.get("page"):
                    page = int(request.args.get("page"))
                    ppl_data = api_movie.search_ppl(ppl_name, int(request.args.get("page")))
                    return render_template("search.html", page=page, name=ppl_name, s="actors", actor=ppl_data,
                                           nimg=NIMG, img=IMG)
                else:
                    ppl_data = api_movie.search_ppl(ppl_name, 1)
                    return render_template("search.html", page=1, name=ppl_name, s="actors", actor=ppl_data, nimg=NIMG,
                                           img=IMG)
            elif "name" in request.args and "page" in request.args:
                page = int(request.args.get("page"))
                ppl_name = request.args.get("name")
                ppl_data = api_movie.search_ppl(ppl_name, page)
                return render_template("search.html", name=ppl_name, s="actors", actor=ppl_data, nimg=NIMG, img=IMG)
            return render_template("search.html", s="actors")


        elif request.args.get("s") == "model":
            if request.method == "POST":
                model_name = request.form.get("movie")
                if request.args.get("page"):
                    page = int(request.args.get('page'))
                    movie_data = scraping.search_offline(all_porn_stars, model_name, page)
                    return render_template("search.html", page=page, name=model_name, s="model", models=movie_data,
                                           nimg=NIMG, img=IMG)
                else:
                    page = 1
                    movie_data = scraping.search_offline(all_porn_stars, model_name, page)
                    return render_template("search.html", page=page, name=model_name, s="model", models=movie_data,
                                           nimg=NIMG, img=IMG)
            elif "name" in request.args and "page" in request.args:
                page = int(request.args.get("page"))
                model_name = request.args.get("name")
                movie_data = scraping.search_offline(all_porn_stars, model_name, page)
                return render_template("search.html", page=page, name=model_name, s="model", models=movie_data,
                                       nimg=NIMG, img=IMG)
            return render_template("search.html", s="model")
    else:
        if request.method == "POST":
            search = request.form.get("movie")
            if "page" in request.args:
                page = int(request.args.get("page"))
                search_data = api_movie.search_all(search, page)
                return render_template("search.html", name=search, page=page, all=search_data, img=IMG, nimg=NIMG)

            else:
                page = 1
                search_data = api_movie.search_all(search, page)
                return render_template("search.html", name=search, page=page, all=search_data, img=IMG, nimg=NIMG)

        elif "page" and "name" in request.args:
            page = int(request.args.get("page"))
            search = request.args.get("name")
            search_data = api_movie.search_all(search, page)
            return render_template("search.html", name=search, page=page, all=search_data, img=IMG, nimg=NIMG)

    """ adding methods """
    if "movie_id" in request.args:
        if request.args.get("media") == "movie":
            movie_id = request.args.get("movie_id")
            movie_data = api_movie.movie_data(movie_id)
            new_movie = Movie(name=movie_data[0], url=movie_data[3], user_id=current_user.id)
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
        elif request.args.get("media") == "tv":
            movie_id = request.args.get("movie_id")
            tv_data = api_movie.tv_data(movie_id)
            new_movie = Tv(name=tv_data[0], url=tv_data[2], user_id=current_user.id)
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
        elif request.args.get("media") == "pp":
            movie_id = request.args.get("movie_id")
            movie_data = api_movie.ppl_data(movie_id)
            new_movie = Actor(name=movie_data[0], url=movie_data[1], user_id=current_user.id)
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")

        elif request.args.get("media") == "model":
            model_name = unquote(request.args.get('n'))
            model_url = request.args.get("u")
            new_movie = Model(name=model_name, url=model_url, user_id=current_user.id)
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
    return render_template("search.html", nimg=NIMG, img=IMG)


@app.route("/discover/<content>/<int:page>")
@login_required
def discover(page, content):
    if page is None:
        page = 1
    if content is None:
        content = "movie"

    if content == "movie":
        data = api_movie.discover_movies(page)
        content = "movie"
    elif content == "tv":
        data = api_movie.discover_tv(page)
        content = "tv"
    else:
        data = scraping.all_porn_stars(page)
        content = "model"

    if "nav" in request.args:
        if request.args.get("nav") == "back":
            if page in range(0, 11):
                page = 1
                start = 1
                end = 11
                r = range(start, end)
                return redirect(url_for("discover", r=r, content=content, page=page))
            else:
                page = page - 10
                start = page - 10
                end = page
                r = range(start, end)
                return redirect(url_for("discover", r=r, content=content, page=page))
        else:
            page = page + 1
            start = page + 1
            end = page + 11
            r = range(start, end)
            return redirect(url_for("discover", r=r, page=page, content=content))
    else:
        start = page
        end = page + 10

    r = range(start, end)
    return render_template("index.html", r=r, page=page, content=content, movies=data, nimg=NIMG, img=IMG)


@app.route("/movies")
@login_required
def movie():
    all_movies = db.session.query(Movie).filter(Movie.user_id == current_user.id).all()
    if "movie_id" in request.args:
        deleted_movie = db.session.query(Movie).filter(Movie.id == request.args.get("movie_id")).first()
        db.session.delete(deleted_movie)
        db.session.commit()
        return redirect("/movies")
    return render_template("movies.html", movies=all_movies)


@app.route("/tv")
@login_required
def tv():
    all_tv = db.session.query(Tv).filter(Tv.user_id == current_user.id).all()
    if "movie_id" in request.args:
        deleted_movie = db.session.query(Tv).filter(Tv.id == request.args.get("movie_id")).first()
        db.session.delete(deleted_movie)
        db.session.commit()
        return redirect("/tv")
    return render_template("movies.html", tv=all_tv)


@app.route("/actors")
@login_required
def actor():
    all_actors = db.session.query(Actor).filter(Actor.user_id == current_user.id).all()
    if "movie_id" in request.args:
        deleted_movie = db.session.query(Actor).filter(Actor.id == request.args.get("movie_id")).first()
        db.session.delete(deleted_movie)
        db.session.commit()
        return redirect("/actors")
    return render_template("movies.html", actor=all_actors)


@app.route("/models")
@login_required
def model():
    all_models = db.session.query(Model).filter(Model.user_id == current_user.id).all()
    if "movie_id" in request.args:
        deleted_movie = db.session.query(Model).filter(Model.id == request.args.get("movie_id")).first()
        db.session.delete(deleted_movie)
        db.session.commit()
        return redirect("/models")
    return render_template("movies.html", model=all_models)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
