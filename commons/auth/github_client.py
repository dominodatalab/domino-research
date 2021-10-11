import os
import auth
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, Response

BASE_URL = "https://github.com/login/oauth"
USER_INFO_URL = "https://api.github.com/user"


class GithubLoginManager(auth.LoginManager):
    callback_uri = None

    def __init__(self, app):
        super().__init__(app)
        self.oauth = OAuth(app)
        self.oauth.register(
            "github",
            client_id=os.environ[auth.OAUTH_CLIENT_ID],
            client_secret=os.environ[auth.OAUTH_CLIENT_SECRET],
            access_token_url=BASE_URL + "/access_token",
            authorize_url=BASE_URL + "/authorize",
            client_kwargs={"scope": "openid profile email"},
        )

    def login(self):
        if self.callback_uri is None:
            raise RuntimeError("Authentication callback URI is not set")
        ext_uri = auth.externalize(self.callback_uri)
        return self.oauth.github.authorize_redirect(ext_uri)

    def auth_callback(self):
        try:
            token = self.oauth.github.authorize_access_token()
            self.logger.debug(f"Obtained token: {token}.")
            resp = self.oauth.github.get(USER_INFO_URL)
            user_info = resp.json()
            self.logger.debug(f"Obtained user info: {user_info}.")
            user_name = user_info["login"]
            princ = {
                auth.PRINCIPAL_PROVIDER_KEY: "github",
                auth.PRINCIPAL_ID_KEY: user_info["id"],
                auth.PRINCIPAL_NAME_KEY: user_name,
            }
            email = user_info["email"]
            if email is not None:
                princ[auth.PRINCIPAL_EMAIL_KEY] = email
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
        self.logger.info(f"User '{user_name}' logged out.")
        # Github provides no API for a server-side logout
        return redirect(redirect_url)
