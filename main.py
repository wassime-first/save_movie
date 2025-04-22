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
import games_api


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

""" tables """

class User(UserMixin, db.Model):
    __tablename__ = "users_saves"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)
    models = db.relationship("Model", backref="user", cascade="all, delete, save-update")
    tvs = db.relationship("Tv", backref="user", cascade="all, delete, save-update")
    actors = db.relationship("Actor", backref="user", cascade="all, delete, save-update")
    movies = db.relationship("Movie", backref="user", cascade="all, delete, save-update")
    custom = db.relationship("Custom", backref="user", cascade="all, delete, save-update")
    games = db.relationship("Game", backref="user", cascade="all, delete, save-update")


class Custom(UserMixin, db.Model):
    __tablename__ = "users_custom"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)
    watch_url = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_saves.id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)


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

class Game(UserMixin, db.Model):
    __tablename__ = "games"
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

""" flask forms """

class MovieForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Search")


class CustomForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    img = URLField("Img Url", validators=[DataRequired()])
    watch = URLField("Watch Url", validators=[DataRequired()])
    submit = SubmitField("Add")

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
                    page = request.args.get('page')
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

        elif request.args.get("s") == "games":
            if request.method == "POST":
                game_name = request.form.get("movie")
                if "page" in request.args:
                    page = int(request.args.get("page"))
                    tv_data = games_api.search_games(game_name, page)
                    return render_template("search.html", name=game_name, page=page, s="games", game=tv_data, nimg=NIMG,
                                           img=IMG)
                else:
                    page = 1
                    tv_data = games_api.search_games(game_name, page)
                    return render_template("search.html", name=game_name, page=page, s="games", game=tv_data, nimg=NIMG,
                                           img=IMG)
            elif "page" and "name" in request.args:
                page = int(request.args.get("page"))
                game_name = request.args.get("name")
                tv_data = games_api.search_games(game_name, page)
                return render_template("search.html", name=game_name, page=page, s="games", game=tv_data, nimg=NIMG,
                                           img=IMG)
        return render_template("search.html", s="games")

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
            all_movies = db.session.query(Movie).filter(Movie.user_id == current_user.id).all()
            if int(movie_id) in [int(m.id) for m in all_movies]:
                return redirect("/")
            else:
                new_movie = Movie(id=movie_id, name=movie_data[0], url=movie_data[3], user_id=current_user.id)
                db.session.add(new_movie)
                db.session.commit()
                return redirect("/")
        elif request.args.get("media") == "tv":
            movie_id = request.args.get("movie_id")
            tv_data = api_movie.tv_data(movie_id)
            all_tv = db.session.query(Tv).filter(Tv.user_id == current_user.id).all()
            if int(movie_id) in [int(m.id) for m in all_tv]:
                return redirect("/")
            else:
                new_movie = Tv(id=movie_id, name=tv_data[0], url=tv_data[2], user_id=current_user.id)
                db.session.add(new_movie)
                db.session.commit()
                return redirect("/")
        elif request.args.get("media") == "pp":
            movie_id = request.args.get("movie_id")
            movie_data = api_movie.ppl_data(movie_id)
            all_actors = db.session.query(Actor).filter(Actor.user_id == current_user.id).all()
            if movie_data[0] in [m.name for m in all_actors]:
                return redirect("/")
            else:
                new_movie = Actor(id=movie_id, name=movie_data[0], url=movie_data[1], user_id=current_user.id)
                db.session.add(new_movie)
                db.session.commit()
                return redirect("/")

        elif request.args.get("media") == "model":
            model_name = unquote(request.args.get('n'))
            model_url = request.args.get("u")
            all_models = db.session.query(Model).filter(Model.user_id == current_user.id).all()
            if model_name in [m.name for m in all_models]:
                return redirect("/")
            else:
                new_movie = Model(name=model_name, url=model_url, user_id=current_user.id)
                db.session.add(new_movie)
                db.session.commit()
                return redirect("/")

        elif request.args.get("media") == "game":
            movie_id = request.args.get("movie_id")
            game_name = unquote(request.args.get('n'))
            game_url = request.args.get("u")
            all_games = db.session.query(Game).filter(Game.user_id == current_user.id).all()
            if int(movie_id) in [int(m.id) for m in all_games]:
                return redirect("/")
            else:
                new_game = Game(id=movie_id, name=game_name, url=game_url, user_id=current_user.id)
                db.session.add(new_game)
                db.session.commit()
                return redirect("/")

    return render_template("search.html", nimg=NIMG, img=IMG)


@app.route("/discover/<content>/<int:page>")
@login_required
def discover(page, content):
    all_names = []
    tabeles = (Actor, Model, Movie, Tv)
    for i in tabeles:
        data = db.session.query(i).filter_by(user_id=current_user.id).all()
        for n in data:
            all_names.append(n.name)
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
    return render_template("index.html", names=all_names, r=r, page=page, content=content, movies=data, nimg=NIMG, img=IMG)


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

@app.route("/game", methods=["POST", "GET"])
@login_required
def game():
    all_games = db.session.query(Game).filter(Game.user_id == current_user.id).all()
    if "game_id" in request.args:
        deleted_movie = db.session.query(Game).filter(Game.id == request.args.get("game_id")).first()
        db.session.delete(deleted_movie)
        db.session.commit()
        return redirect("/game")
    return render_template("movies.html", game=all_games)

@app.route("/custom", methods=["POST", "GET"])
@login_required
def custom():
    form = CustomForm()
    all_custom = db.session.query(Custom).filter(Custom.user_id == current_user.id).all()
    if form.validate_on_submit():
        name = form.name.data
        img = form.img.data
        watch = form.watch.data
        new_custom = Custom(name=name, img_url=img, watch_url=watch, user_id=current_user.id)
        db.session.add(new_custom)
        db.session.commit()
        return redirect("custom")
    if "custom_id" in request.args:
        deleted_custom = db.session.query(Custom).filter(Custom.id == request.args.get("custom_id")).first()
        db.session.delete(deleted_custom)
        db.session.commit()
        return redirect("custom")
    if "add" in request.args:
        return render_template("custom.html", form=form)
    return render_template( "movies.html", custom=all_custom)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("login")


@app.route("/details/<media>")
@login_required
def details(media):
    if request.path.startswith('/details/movie') or media == "movie":
        movie_id = request.args.get("movie_id")
        data = api_movie.movie_data(movie_id)
        images = api_movie.movie_image_data(movie_id)
        videos = api_movie.movie_video_data(
            movie_id)
        return render_template("details.html", images=images, movie=data, videos=videos)
    elif request.path.startswith('/details/tv') or media == 'tv':
        movie_id = request.args.get("movie_id")
        data = api_movie.tv_data(movie_id)
        images = api_movie.tv_image_data(movie_id)
        videos = api_movie.tv_video_data(
            movie_id)
        return render_template("details.html", images=images, movie=data, videos=videos)
    elif request.path.startswith('/details/game') or media == 'game':
        movie_id = request.args.get("movie_id")
        data = games_api.game_data(movie_id)
        images = data[2]
        videos = games_api.game_trailers(
            int(movie_id))
        return render_template("details.html", images=images, movie=data, videos=videos)

    return render_template("details.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
