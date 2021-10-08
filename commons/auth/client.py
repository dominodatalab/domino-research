import os
from functools import wraps
from flask import session, redirect, request
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode


def externalize(uri):
    if uri.startswith("http"):
        return uri
    return request.host_url.removesuffix("/") + uri


BASE_URL = os.environ["OAUTH_URL"]


class LoginManager(object):
    def __init__(self, app):
        self.oauth = OAuth(app)
        self.oauth.register(
            "client",
            client_id=os.environ["OAUTH_CLIENT_ID"],
            client_secret=os.environ["OAUTH_CLIENT_SECRET"],
            api_base_url=BASE_URL,
            server_metadata_url=BASE_URL + "/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile email"},
        )
        self.callback_uri = None

    def login(self):
        if self.callback_uri is None:
            raise RuntimeError("Authentication callback URI is not set")
        ext_uri = externalize(self.callback_uri)
        return self.oauth.client.authorize_redirect(ext_uri)

    def auth_callback(self):  # TODO Error handling
        self.oauth.client.authorize_access_token()
        resp = self.oauth.client.get("userinfo")
        userinfo = resp.json()
        print(f"{userinfo}")
        session["profile"] = {
            "id": userinfo["sub"],
            "name": userinfo["nickname"],
            "email": userinfo["email"],
        }
        return redirect(session.pop("stored-request-path", "/"))

    def logout(self, redirect_uri):
        session.clear()
        params = {
            "returnTo": externalize(redirect_uri),
            "client_id": self.oauth.client.client_id,
        }
        return redirect(
            self.oauth.client.api_base_url + "/v2/logout?" + urlencode(params)
        )

    def auth_required(self, f):
        @wraps(f)
        def assure_auth(*args, **kwargs):
            if "profile" not in session:
                if request.path:
                    session["stored-request-path"] = request.path
                return self.login()
            return f(*args, **kwargs)

        return assure_auth
