import auth
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, Response
from six.moves.urllib.parse import urlencode
from flask import Flask


LOGIN_TYPE = "auth0"
USER_INFO_URL = "userinfo"


class Auth0LoginManager(auth.LoginManager):
    callback_uri = None

    def __init__(self, app: Flask, conf: dict[str, str]):
        super().__init__(app, conf)

        self.base_url = conf.get(auth.OAUTH_BASE_URL, None)
        if not self.base_url:
            raise RuntimeError("Auth0 base URL is not set")
        config_url = self.base_url + "/.well-known/openid-configuration"

        client_id = conf.get(auth.OAUTH_CLIENT_ID, None)
        client_secret = conf.get(auth.OAUTH_CLIENT_SECRET, None)
        if (not client_id) or (not client_secret):
            raise RuntimeError("OAuth client configuration is not set")

        self.oauth = OAuth(app)
        self.oauth.register(
            LOGIN_TYPE,
            client_id=client_id,
            client_secret=client_secret,
            api_base_url=self.base_url,
            server_metadata_url=config_url,
            client_kwargs={"scope": "openid profile email"},
        )
        self.logger.info(f"Created {LOGIN_TYPE} login manager")

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
                auth.PRINCIPAL_PROVIDER_KEY: LOGIN_TYPE,
                auth.PRINCIPAL_ID_KEY: user_info["sub"],
                auth.PRINCIPAL_NAME_KEY: user_name,
            }
            if user_info.get("email_verified", False):
                princ[auth.PRINCIPAL_EMAIL_KEY] = user_info["email"]
            if not self.validate_principal(princ):
                return Response("User Not Permitted", 401)
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
        return redirect(
            "{}/v2/logout?{}".format(self.base_url, urlencode(params))
        )

    def __str__(self):
        return LOGIN_TYPE
