import bcrypt
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for, session

from .db import get_db

bp = Blueprint("account", __name__, url_prefix="/account")

def user_required(view):
    """
    Tiny wrapper only for this blueprint that prevents logged out users from
    accessing the password change pages. We don't use the standard @login_required
    wrapper here because it would cause a redirect loop if we did.
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not "user" in session:
            flash("You must be logged in for that.")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped_view

@bp.route("/password")
@user_required
def password():
    return render_template("password.html")

@bp.route("/password/change", methods=["POST"])
@user_required
def password_change():
    db = get_db()

    active_user = session["user"]["username"]
    submitted_password = request.form["password"]

    user = db.execute(
        "SELECT password FROM users WHERE username = ?", (active_user,)
    ).fetchone()

    success = bcrypt.checkpw(submitted_password.encode("utf-8"), user["password"])

    if not success:
        flash("Old password was incorrect. Please try again.")
        return redirect(url_for("account.password"))

    if request.form["password1"] != request.form["password2"]:
        flash("Passwords did not match. Please try again.")
        return redirect(url_for("account.password"))
    
    if request.form["password"] == request.form["password1"]:
        flash("Old and new passwords can't be the same.")
        return redirect(url_for("account.password"))

    # TODO: Password strength checking

    pw_hashed = bcrypt.hashpw(request.form["password1"].encode("utf-8"), bcrypt.gensalt())

    db.execute(
        "UPDATE users SET password = ?, pw_chg_req = 0 WHERE username = ?;",
        (pw_hashed, active_user)
    )

    db.commit()

    session["user"]["pw_chg_req"] = False
    # Banged my head on a wall for a while on this one.
    # https://flask.palletsprojects.com/en/2.1.x/api/#flask.session.modified
    session.modified = True

    return redirect(url_for("index"))
