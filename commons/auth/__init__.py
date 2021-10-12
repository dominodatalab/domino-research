from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional
from flask import Flask, Response, session, request
import logging
import re

PRINCIPAL_KEY = "principal"  # Points to a Principal dict (see below)
STORED_REQUEST_PATH_KEY = "stored-request-path"  # Internal use only

# Dictionary keys pertaining to Principal.
# We can't use a "real" class here, because arbitrary classes
# are apparently not supported as Flask session values.
PRINCIPAL_ID_KEY = "id"
PRINCIPAL_PROVIDER_KEY = "provider"
PRINCIPAL_NAME_KEY = "name"
PRINCIPAL_EMAIL_KEY = "email"

# Common configuration variables.
LOGIN_TYPE = "login-type"
OAUTH_BASE_URL = "oauth-base-url"
OAUTH_CLIENT_ID = "oauth-client-id"
OAUTH_CLIENT_SECRET = "oauth-client-secret"
ALLOWED_DOMAINS = "allowed-domains"
ALLOWED_USERS = "allowed-users"


class LoginManager(ABC):
    allowed_domains = None
    allowed_users = None

    def __init__(self, app: Flask, conf: dict[str, str]):
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

        if s := conf.get(ALLOWED_DOMAINS, None):
            self.allowed_domains = set[str](
                [s.strip().casefold() for s in s.split(",")]
            )
            self.logger.debug(f"Allowed domains: {self.allowed_domains}")

        if s := conf.get(ALLOWED_USERS, None):
            self.allowed_users = set[str](
                [s.strip().casefold() for s in s.split(",")]
            )
            self.logger.debug(f"Allowed users: {self.allowed_users}")

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

    def validate_principal(self, princ: dict[str, str]) -> bool:
        """Validating a user principal against a list of allowed
        users and email domains."""
        user = princ.get(PRINCIPAL_NAME_KEY)

        if self.allowed_users:
            if user.casefold() not in self.allowed_users:
                self.logger.info(f"User {user} is not allowed")
                return False

        if self.allowed_domains:
            email = princ.get(PRINCIPAL_EMAIL_KEY, None)
            if not email:
                self.logger.info(f"User {user} has no email")
                return False
            match = re.match(r"(\S+)@(\S+)", email)
            if not match:
                self.logger.info(f"User {user} has an invalid email")
                return False
            domain = match.group(2)
            if domain.casefold() not in self.allowed_domains:
                self.logger.info(
                    f"User {user} is not from the allowed domains"
                )
                return False

        return True


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
