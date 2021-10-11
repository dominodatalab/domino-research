from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional
from flask import Response, session, request
import logging

# Web session keys.
PRINCIPAL_KEY = "principal"  # Points to a Principal dict (see below)
STORED_REQUEST_PATH_KEY = "stored-request-path"  # Internal use only

# Dictionary keys pertaining to Principal.
# We can't use a "real" class here, because arbitrary classes
# are apparently not supported as Flask session values.
PRINCIPAL_ID_KEY = "id"
PRINCIPAL_PROVIDER_KEY = "provider"
PRINCIPAL_NAME_KEY = "name"
PRINCIPAL_EMAIL_KEY = "email"

# Common configuration variable.
OAUTH_CLIENT_ID = "OAUTH_CLIENT_ID"
OAUTH_CLIENT_SECRET = "OAUTH_CLIENT_SECRET"


class LoginManager(ABC):
    def __init__(self, app):
        if app.debug:
            app.logger.setLevel(logging.DEBUG)
        else:
            gunicorn_logger = logging.getLogger("gunicorn.error")
            if gunicorn_logger.handlers:
                app.logger.handlers = gunicorn_logger.handlers
                app.logger.setLevel(gunicorn_logger.level)
            else:
                app.logger.setLevel(logging.INFO)
        self.logger = app.logger

    @abstractmethod
    def login(self) -> Response:
        """Initiates a user login workflow."""
        pass

    @abstractmethod
    def auth_callback(self) -> Response:
        """Internal endpoint called upon completion of the login workflow.
        Validates user credentials and sets the user principal object into
        the web session."""
        pass

    @abstractmethod
    def logout(self, redirect_url: str) -> Response:
        """Initiates the user logout workflow."""
        pass

    def auth_required(self, f):
        """Function decorator for marking HTTP routes that require
        user authorization."""

        @wraps(f)
        def assure_auth(*args, **kwargs):
            if not is_logged_in():
                if request.path:
                    session[STORED_REQUEST_PATH_KEY] = request.path
                return self.login()
            return f(*args, **kwargs)

        return assure_auth


def externalize(url: str) -> str:
    """Utility function for externalizing a URL."""
    return (
        url
        if url.startswith("http")
        else request.host_url.removesuffix("/") + url
    )


def current_user() -> Optional[str]:
    """Utility function for obtaining a user name from the current context."""
    try:
        return session[PRINCIPAL_KEY][PRINCIPAL_NAME_KEY]
    except KeyError:
        return None


def is_logged_in() -> bool:
    """Utility function for checking of a user is currently logged in."""
    return PRINCIPAL_KEY in session
