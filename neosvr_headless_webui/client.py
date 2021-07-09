from flask import Blueprint, current_app, g, render_template
from .auth import login_required

from rpyc import connect

bp = Blueprint("client", __name__, url_prefix="/client")

def list_headless_clients():
    """Lists headless clients that are currently running and ready."""
    # TODO: This code is duplicated in `dashboard.py`.
    # Could be cleaned up a little.
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    clients = conn.root.list_headless_clients()

    ready_clients = {}
    for c in clients:
        if not clients[c].is_ready():
            continue
        ready_clients[c] = clients[c]
    return ready_clients

@bp.route("/<int:client_id>")
@login_required
def get_client(client_id):
    conn = connect(
        current_app.config["MANAGER_HOST"],
        current_app.config["MANAGER_PORT"]
    )
    try:
        client = conn.root.get_headless_client(client_id)
    except LookupError:
        return ("This client does not exist.", 404) # TODO: Pretty 404
    if not client.is_ready():
        return ("The client is not ready yet. Try again soon.", 404)

    g.clients = list_headless_clients()
    g.client_id = client_id
    g.client_name = client.client_name
    g.worlds = list(enumerate(client.worlds()))
    g.state = client.get_state()
    g.summary = client.summary()
    g.version = client.version
    g.compatibility_hash = client.compatibility_hash
    g.machine_id = client.machine_id
    g.supported_network_protocols = client.supported_network_protocols

    return render_template("client.html")

@bp.route("/<int:client_id>/session/<int:world_number>")
@login_required
def get_session(client_id, world_number):
    conn = connect(
        current_app.config["MANAGER_HOST"],
        current_app.config["MANAGER_PORT"]
    )
    try:
        client = conn.root.get_headless_client(client_id)
    except LookupError:
        return ("This client does not exist.", 404) # TODO: Pretty 404
    if not client.is_ready():
        return ("The client is not ready yet. Try again soon.", 404)

    worlds = client.worlds()
    # Lazy way of checking for valid world numbers.
    if world_number > len(worlds) - 1:
        return ("This session does not exist.", 404)

    g.clients = list_headless_clients()
    g.client_id = client_id
    g.world_number = world_number
    g.client_name = client.client_name
    g.worlds = list(enumerate(worlds))
    g.state = client.get_state()
    g.status = client.status(world=world_number)
    g.users = client.users(world=world_number)
    g.session_url = client.session_url(world=world_number)
    g.version = client.version

    return render_template("session.html")
