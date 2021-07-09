from flask import Blueprint, current_app, g, render_template
from .auth import login_required

from rpyc import connect

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("")
@login_required
def dashboard():
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    g.clients = conn.root.list_headless_clients()
    g.clients_states = {}
    for c in g.clients:
        g.clients_states[c] = g.clients[c].get_state()
    g.status = conn.root.get_manager_status()
    return render_template("dashboard.html")
