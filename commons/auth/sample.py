import os

from flask import (
    Flask,
    render_template,
    url_for,
)  # type: ignore

from auth.auth0_client import Auth0LoginManager
from auth.github_client import GithubLoginManager

app = Flask(__name__)
app.secret_key = os.urandom(16)  # Different key for every runtime

login_manager = Auth0LoginManager(app)
# login_manager = GithubLoginManager(app)
login_manager.callback_uri = "/auth"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return login_manager.login()


@app.route("/auth")
def auth_callback():
    return login_manager.auth_callback()


@app.route("/logout")
def logout():
    return login_manager.logout(url_for("home"))


@app.route("/protected")
@login_manager.auth_required
def protected():
    return render_template("protected.html")
