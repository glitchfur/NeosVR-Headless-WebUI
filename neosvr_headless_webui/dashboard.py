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
    clients = conn.root.list_headless_clients()

    # Filter out clients that are not ready yet.
    g.clients = {}
    for c in clients:
        if not clients[c].ready.is_set():
            continue
        g.clients[c] = clients[c]

    g.status = conn.root.get_manager_status()
    return render_template("dashboard.html")
