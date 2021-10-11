from flask import Flask
from auth import LoginManager, LOGIN_TYPE
import auth.auth0_client
import auth.github_client
import re

_PROVIDERS = {
    auth.auth0_client.CLIENT_TYPE: auth.auth0_client.Auth0LoginManager,
    auth.github_client.CLIENT_TYPE: auth.github_client.GithubLoginManager
}


def create_login_manager(app: Flask, config_name: str) -> LoginManager:
    config = {}
    with open(config_name) as config_file:
        for s in config_file:
            if m := re.match(r"^\s*([a-z0-9_-]+)\s*=\s*(\w+)\s*$", s, re.I):
                config[m.group(1)] = m.group(2)

    login_type = config.get(LOGIN_TYPE, None)
    if not login_type:
        raise RuntimeError(f"Missing '{LOGIN_TYPE}' property")

    login_manager = _PROVIDERS.get(login_type, None)
    if not login_manager:
        raise RuntimeError(f"Unknown login type: {login_type}")

    return login_manager(app)
