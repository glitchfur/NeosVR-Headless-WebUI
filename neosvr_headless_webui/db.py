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
            os.path.join(
                current_app.instance_path,
                current_app.config["DB_NAME"]
            ),
            detect_types=sqlite3.PARSE_DECLTYPES
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

user_cli = AppGroup("user", help="User management commands.")

@user_cli.command("create")
@click.argument("username")
@with_appcontext
def create_user_command(username):
    """Create a new user."""
    db = get_db()

    pw_plain = "".join(secrets.choice(ALPHANUMERIC) for i in range(8))
    pw_hashed = bcrypt.hashpw(pw_plain.encode("utf-8"), bcrypt.gensalt())

    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?);",
        (username, pw_hashed)
    )

    db.commit()

    click.echo("User %s created, password: %s" % (username, pw_plain))

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

    db.execute(
        "DELETE FROM users WHERE username = ?;", (username,)
    )

    db.commit()

    click.echo("User %s deleted" % username)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(user_cli)
