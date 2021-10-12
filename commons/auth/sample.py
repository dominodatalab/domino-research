import os

from flask import (
    Flask,
    render_template,
)  # type: ignore

import auth
import auth.login_factory as factory

app = Flask(__name__)
app.secret_key = os.urandom(16)  # Different key for every runtime

# Location of the access control configuration file
CONF = "/tmp/sample.policy"

login_manager = factory.create_login_manager(app, CONF)

# HTTP Path routed to login_manager.auth_callback()
login_manager.callback_uri = "/auth"

# The three methods below -- login, auth, and logout -- are responsible
# for authenticating the user and handling credential needed for
# further access control


@app.route("/login")
def login():
    """This endpoint can be explicitly called when the user
    need to authenticate"""
    return login_manager.login()


@app.route("/auth")  # The one specified in login_manager.callback_uri
def auth_callback():
    """This endpoint is used by the user provider upon
    completion of the authentication workflow."""
    return login_manager.auth_callback()


@app.route("/logout")
def logout():
    """This endpoint may be called to log the used out."""
    return login_manager.logout("/")


# The following methods are used only as an example.


@app.route("/")
def home():
    """Public endpoint not requiring authentication."""
    print(f"current-user: {auth.current_user()}")
    return render_template("home.html")


@app.route("/protected")
@login_manager.auth_required
def protected():
    """Protected endpoint accessible only for authenticated users."""
    return render_template("protected.html")
