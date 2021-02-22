from flask import Flask, redirect, render_template, session, url_for
from neosvr_headless_webui.auth import login_required

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    @app.route("/")
    def index():
        if "user" in session:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    from . import auth
    auth.init_oauth(app)
    app.register_blueprint(auth.bp)

    return app
