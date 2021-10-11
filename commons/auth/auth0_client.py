import os
from flask import session, redirect, request
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

import auth

BASE_URL = os.environ["OAUTH_URL"]


class Auth0LoginManager(auth.LoginManager):
    def __init__(self, app):
        self.oauth = OAuth(app)
        self.oauth.register(
            "auth0",
            client_id=os.environ[auth.OAUTH_CLIENT_ID],
            client_secret=os.environ[auth.OAUTH_CLIENT_SECRET],
            api_base_url=BASE_URL,
            server_metadata_url=BASE_URL + "/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile email"},
        )
        self.callback_uri = None

    def login(self):
        if self.callback_uri is None:
            raise RuntimeError("Authentication callback URI is not set")
        ext_uri = auth.externalize(self.callback_uri)
        return self.oauth.auth0.authorize_redirect(ext_uri)

    def auth_callback(self):  # TODO Error handling
        self.oauth.auth0.authorize_access_token()
        resp = self.oauth.auth0.get("userinfo")
        userinfo = resp.json()
        print(f"{userinfo}")
        princ = {
            auth.PRINCIPAL_ID_KEY: userinfo["sub"],
            auth.PRINCIPAL_PROVIDER_KEY: "auth0",
            auth.PRINCIPAL_NAME_KEY: userinfo["name"],
        }
        if userinfo.get("email_verified", False):
            princ[auth.PRINCIPAL_EMAIL_KEY] = userinfo["email"]
        print(f"++{type(princ)} {princ}")
        session[auth.PRINCIPAL_KEY] = princ
        return redirect(session.pop(auth.STORED_REQUEST_PATH_KEY, "/"))

    def logout(self, redirect_uri):
        # Safely removes the session keys associated with the login
        session.pop(auth.PRINCIPAL_KEY, None)
        session.pop(auth.STORED_REQUEST_PATH_KEY, None)
        params = {
            "returnTo": auth.externalize(redirect_uri),
            "client_id": self.oauth.client.client_id,
        }
        return redirect(BASE_URL + "/v2/logout?" + urlencode(params))
