import auth
from authlib.integrations.flask_client import OAuth
from flask import Flask, session, redirect, Response

LOGIN_TYPE = "github"
BASE_URL = "https://github.com/login/oauth"
USER_INFO_URL = "https://api.github.com/user"


class GithubLoginManager(auth.LoginManager):
    callback_uri = None

    def __init__(self, app: Flask, conf: dict[str, str]):
        super().__init__(app, conf)

        client_id = conf.get(auth.OAUTH_CLIENT_ID, None)
        client_secret = conf.get(auth.OAUTH_CLIENT_SECRET, None)
        if (not client_id) or (not client_secret):
            raise RuntimeError("OAuth client configuration is not set")

        self.oauth = OAuth(app)
        self.oauth.register(
            LOGIN_TYPE,
            client_id=client_id,
            client_secret=client_secret,
            access_token_url=BASE_URL + "/access_token",
            authorize_url=BASE_URL + "/authorize",
            client_kwargs={"scope": "openid profile email"},
        )
        self.logger.info(f"Created {LOGIN_TYPE} login manager")

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
                auth.PRINCIPAL_PROVIDER_KEY: LOGIN_TYPE,
                auth.PRINCIPAL_ID_KEY: user_info["id"],
                auth.PRINCIPAL_NAME_KEY: user_name,
            }
            email = user_info["email"]
            if email:
                princ[auth.PRINCIPAL_EMAIL_KEY] = email
            self.logger.info(f"User '{user_name}' logged in")
            session[auth.PRINCIPAL_KEY] = princ
            return redirect(session.pop(auth.STORED_REQUEST_PATH_KEY, "/"))
        except Exception:
            session.pop(auth.STORED_REQUEST_PATH_KEY, None)
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

    def __str__(self):
        return LOGIN_TYPE
