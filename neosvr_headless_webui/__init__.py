from flask import Flask, redirect, render_template, session, url_for
from .auth import login_required

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    @app.route("/")
    def index():
        if "user" in session:
            return redirect(url_for("dashboard.dashboard"))
        return render_template("index.html")

    from . import dashboard
    app.register_blueprint(dashboard.bp)

    from . import auth
    auth.init_oauth(app)
    app.register_blueprint(auth.bp)

    from . import api
    app.register_blueprint(api.bp)

    from . import client
    app.register_blueprint(client.bp)

    return app
