from flask import Blueprint, current_app, g, render_template
from .auth import login_required

from rpyc import connect

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Maximum time to wait for RPC responses (in seconds)
SYNC_REQUEST_TIMEOUT = 60

def connect_manager():
    """Returns an RPC connection to the manager server."""
    return connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"],
        config={"sync_request_timeout": SYNC_REQUEST_TIMEOUT}
    )

@bp.route("")
@login_required
def dashboard():
    conn = connect_manager()
    g.clients = conn.root.list_headless_clients()
    g.clients_states = {}
    for c in g.clients:
        g.clients_states[c] = g.clients[c].get_state()
    g.status = conn.root.get_manager_status()
    return render_template("dashboard.html")
