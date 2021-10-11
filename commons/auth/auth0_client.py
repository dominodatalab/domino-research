import os
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, Response
from six.moves.urllib.parse import urlencode

import auth

BASE_URL = os.environ.get("OAUTH_URL", None)
USER_INFO_URL = "userinfo"


class Auth0LoginManager(auth.LoginManager):
    callback_uri = None

    def __init__(self, app):
        super().__init__(app)
        self.oauth = OAuth(app)
        if BASE_URL is None:
            raise RuntimeError("Auth0 base URI is not set")
        metadata_url = BASE_URL + "/.well-known/openid-configuration"
        self.oauth.register(
            "auth0",
            client_id=os.environ[auth.OAUTH_CLIENT_ID],
            client_secret=os.environ[auth.OAUTH_CLIENT_SECRET],
            api_base_url=BASE_URL,
            server_metadata_url=metadata_url,
            client_kwargs={"scope": "openid profile email"},
        )

    def login(self):
        if self.callback_uri is None:
            raise RuntimeError("Authentication callback URI is not set")
        ext_uri = auth.externalize(self.callback_uri)
        return self.oauth.auth0.authorize_redirect(ext_uri)

    def auth_callback(self):
        try:
            token = self.oauth.auth0.authorize_access_token()
            self.logger.debug(f"Obtained token: {token}.")
            resp = self.oauth.auth0.get("userinfo")
            user_info = resp.json()
            self.logger.debug(f"Obtained user info: {user_info}.")
            user_name = user_info["name"]
            princ = {
                auth.PRINCIPAL_PROVIDER_KEY: "auth0",
                auth.PRINCIPAL_ID_KEY: user_info["sub"],
                auth.PRINCIPAL_NAME_KEY: user_name,
            }
            if user_info.get("email_verified", False):
                princ[auth.PRINCIPAL_EMAIL_KEY] = user_info["email"]
            self.logger.info(f"User '{user_name}' logged in.")
            session[auth.PRINCIPAL_KEY] = princ
            return redirect(session.pop(auth.STORED_REQUEST_PATH_KEY, "/"))
        except Exception:
            self.logger.exception("User authentication failed")
            return Response("User Authentication Failed", 400)

    def logout(self, redirect_url):
        if not auth.is_logged_in():
            return redirect(redirect_url)
        user_name = session.pop(auth.PRINCIPAL_KEY)[auth.PRINCIPAL_NAME_KEY]
        session.pop(auth.STORED_REQUEST_PATH_KEY, None)
        params = {
            "returnTo": auth.externalize(redirect_url),
            "client_id": self.oauth.auth0.client_id,
        }
        self.logger.info(f"User '{user_name}' logged out.")
        return redirect("{}/v2/logout?{}".format(BASE_URL, urlencode(params)))
