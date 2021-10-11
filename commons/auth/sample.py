import os

from flask import (
    Flask,
    render_template,
)  # type: ignore

import auth
import auth.login_factory as factory

app = Flask(__name__)
app.secret_key = os.urandom(16)  # Different key for every runtime

login_manager = factory.create_login_manager(
    app, "/Users/andreypetrov/test.policy"
)
login_manager.callback_uri = "/auth"


@app.route("/")
def home():
    print(f"current-user: {auth.current_user()}")
    return render_template("home.html")


@app.route("/login")
def login():
    return login_manager.login()


@app.route("/auth")
def auth_callback():
    return login_manager.auth_callback()


@app.route("/logout")
def logout():
    return login_manager.logout("/")


@app.route("/protected")
@login_manager.auth_required
def protected():
    return render_template("protected.html")
