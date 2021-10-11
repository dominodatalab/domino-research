from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional

from flask import Response, session, request

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
    @abstractmethod
    def login(self) -> Response:
        pass

    @abstractmethod
    def auth_callback(self) -> Response:
        pass

    @abstractmethod
    def logout(self, redirect_uri) -> Response:
        pass

    def auth_required(self, f):
        @wraps(f)
        def assure_auth(*args, **kwargs):
            if not is_logged_in():
                if request.path:
                    session[STORED_REQUEST_PATH_KEY] = request.path
                return self.login()
            return f(*args, **kwargs)

        return assure_auth


def externalize(uri) -> str:
    if uri.startswith("http"):
        return uri
    return request.host_url.removesuffix("/") + uri


def current_user() -> Optional[str]:
    try:
        return session[PRINCIPAL_KEY][PRINCIPAL_NAME_KEY]
    except KeyError:
        return None


def is_logged_in() -> bool:
    return PRINCIPAL_KEY in session
