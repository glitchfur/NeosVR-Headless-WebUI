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

import os
import sqlite3
import secrets
import string

import bcrypt

import click
from flask import current_app, g
from flask.cli import AppGroup, with_appcontext

ALPHANUMERIC = string.ascii_letters + string.digits


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            os.path.join(current_app.instance_path, current_app.config["DB_NAME"]),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("users.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def _generate_pw(length=8):
    """
    Securely generate an alphanumeric password of the provided `length`.
    Returns a `tuple` in the form `(password: str, hash: bytes)`.
    """
    pw_plain = "".join(secrets.choice(ALPHANUMERIC) for i in range(length))
    pw_hashed = bcrypt.hashpw(pw_plain.encode("utf-8"), bcrypt.gensalt())
    return (pw_plain, pw_hashed)


user_cli = AppGroup("user", help="User management commands.")


@user_cli.command("create")
@click.argument("username")
@with_appcontext
def create_user_command(username):
    """Create a new user."""
    db = get_db()

    pw = _generate_pw()

    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?);", (username, pw[1])
    )

    db.commit()

    click.echo("User %s created, password: %s" % (username, pw[0]))


@user_cli.command("list")
@with_appcontext
def list_user_command():
    """List all users."""
    db = get_db()

    users = db.execute("SELECT username FROM users;")

    for user in users.fetchall():
        click.echo(user["username"])


@user_cli.command("delete")
@click.argument("username")
@with_appcontext
def delete_user_command(username):
    """Delete a user."""
    db = get_db()

    db.execute("DELETE FROM users WHERE username = ?;", (username,))

    db.commit()

    click.echo("User %s deleted" % username)


@user_cli.command("reset-password")
@click.argument("username")
@with_appcontext
def reset_user_password_command(username):
    """Reset a user's password."""
    db = get_db()

    new_pw = _generate_pw()

    db.execute(
        "UPDATE users SET password = ?, pw_chg_req = 1 WHERE username = ?",
        (new_pw[1], username),
    )

    db.commit()

    click.echo("User %s password reset: %s" % (username, new_pw[0]))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(user_cli)
