# NeosVR-Headless-WebUI
# Copyright (C) 2022  GlitchFur

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bcrypt
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, request, session, url_for

from .db import get_db

bp = Blueprint("auth", __name__)

log_action = lambda msg: current_app.logger.info(msg)


def login_required(view):
    """
    Decorator that requires users to be logged in for a view.
    Redirects users to the login page with an error if they are not.
    If they are logged in but a password change is required, they are directed
    to do that instead.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not "user" in session:
            flash("You must be logged in for that.")
            return redirect(url_for("index"))
        if session["user"]["pw_chg_req"]:
            flash("You must change your password before continuing.")
            return redirect(url_for("account.password"))
        return view(*args, **kwargs)

    return wrapped_view


def api_login_required(view):
    """
    Decorator that requires users to be logged in to use an API method.
    Unauthenticated users get a HTTP 401 error and a JSON response.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not "user" in session:
            response = {"success": False, "message": "You must be logged in for that."}
            return response, 401
        return view(*args, **kwargs)

    return wrapped_view


@bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()

    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    # If user doesn't exist, bail out early with a generic message.
    if user == None:
        log_action("(User: %s) Login denied, user does not exist")
        flash("Login incorrect")
        return redirect(url_for("index"))

    success = bcrypt.checkpw(password.encode("utf-8"), user["password"])

    if not success:
        log_action("(User: %s) Login denied, incorrect password" % user["username"])
        flash("Login incorrect")
        return redirect(url_for("index"))

    log_action("(User: %s) Login approved" % user["username"])
    session_data = {
        "id": user["id"],
        "username": user["username"],
        "pw_chg_req": bool(user["pw_chg_req"]),
    }
    session["user"] = session_data

    return redirect(url_for("index"))


@bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))
