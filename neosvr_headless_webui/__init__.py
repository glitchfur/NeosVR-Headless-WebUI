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

import click
from flask import Flask, redirect, render_template, session, url_for

from os import path, urandom
from base64 import b64encode

import logging


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    if app.config["LOG_FILE"]:
        rl = logging.getLogger()
        rl.setLevel("INFO")
        hdlr = logging.FileHandler(app.config["LOG_FILE"])
        fmt = logging.Formatter(
            fmt="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        hdlr.setFormatter(fmt)
        hdlr.addFilter(logging.Filter("neosvr_headless_webui"))
        rl.addHandler(hdlr)

    logo_path = path.join(app.instance_path, app.config["APP_LOGO"])
    if path.exists(logo_path):
        with open(logo_path, "rb") as logo_fp:
            logo_data = b64encode(logo_fp.read()).decode("ascii")
            app.config["APP_LOGO_DATA"] = logo_data

    @app.route("/")
    def index():
        if "user" in session:
            return redirect(url_for("dashboard.dashboard"))
        return render_template("index.html")

    @click.command("gen-secret-key")
    def gen_secret_key_command():
        """Generate a secret key for encrypting session cookies."""
        click.echo(str(repr(urandom(16))))

    from . import db

    db.init_app(app)

    from . import dashboard

    app.register_blueprint(dashboard.bp)

    from . import account

    app.register_blueprint(account.bp)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import api

    app.register_blueprint(api.bp)

    from . import client

    app.register_blueprint(client.bp)

    app.cli.add_command(gen_secret_key_command)

    return app
