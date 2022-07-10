import bcrypt
import requests
from functools import wraps
from hashlib import sha1

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for, session

from .db import get_db
from .auth import login_required

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

@bp.route("/")
@login_required
def account():
    return render_template("account.html")

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

    # Check password hash against Have I Been Pwned breached password list
    # https://haveibeenpwned.com/API/v3#PwnedPasswords

    if current_app.config["PASSWORD_SECURITY_CHECK"]:
        pw_sha1 = sha1(request.form["password1"].encode("utf-8")).hexdigest().upper()
        req = requests.get(
            "https://api.pwnedpasswords.com/range/%s" % pw_sha1[:5],
            headers={"Add-Padding": "True"}
        )
        pws = req.text.split("\r\n")
        for pw in pws:
            h, c = pw.split(":")
            if c == "0": # Skip padding
                continue
            if h == pw_sha1[5:]:
                flash("This password has previously appeared in a data breach and "
                    "is not secure. Please use a more secure password.")
                return redirect(url_for("account.password"))

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
