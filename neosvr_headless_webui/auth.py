from functools import wraps

from flask import Blueprint, current_app, flash, redirect, session, url_for

from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError

bp = Blueprint("auth", __name__)

def init_oauth(app):
    global oauth
    oauth = OAuth(app)
    oauth.register(
        name="concat",
        access_token_url="https://reg.goblfc.org/api/oauth/token",
        authorize_url="https://reg.goblfc.org/oauth/authorize",
        api_base_url="https://reg.goblfc.org/",
        client_kwargs={
            "scope": "pii:basic",
            "token_endpoint_auth_method": "client_secret_post"
        }
    )

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not "user" in session:
            flash("You must be logged in for that.")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped_view

@bp.route("/login")
def login():
    return oauth.concat.authorize_redirect(
        url_for(".authorize", _external=True)
    )

@bp.route("/authorize")
def authorize():
    try:
        # I don't know what the reasoning is for the Web/Flask OAuth client in
        # Authlib sending the "state" parameter when getting the access token.
        # The `requests` client does not do this. In any case, ConCat doesn't
        # like to receive parameters it's not expecting, so it's removed here.
        token = oauth.concat.authorize_access_token(state=None)
    except OAuthError as e:
        if e.error == "access_denied":
            flash("Sorry, authorization is required.")
        else:
            flash("An unknown error occurred.")
        return redirect(url_for("index"))

    user = oauth.concat.get("/api/users/current").json()

    if not user["id"] in current_app.config["AUTHORIZED_USERS"]:
        flash("Access denied")
        return redirect(url_for("index"))

    session_data = {"id": user["id"], "username": user["username"]}
    session["user"] = session_data

    return redirect(url_for("index"))

@bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))
