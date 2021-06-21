from flask import Blueprint, current_app, g, render_template
from .auth import login_required

from rpyc import connect

bp = Blueprint("client", __name__, url_prefix="/client")

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
    if not client.ready.is_set():
        return ("The client is not ready yet. Try again soon.", 404)
    g.client_id = client_id
    g.client_name = client.client_name
    g.worlds = list(enumerate(client.worlds()))
    g.summary = client.summary()
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
    if not client.ready.is_set():
        return ("The client is not ready yet. Try again soon.", 404)

    worlds = client.worlds()
    # Lazy way of checking for valid world numbers.
    if world_number > len(worlds) - 1:
        return ("This session does not exist.", 404)

    g.client_id = client_id
    g.world_number = world_number
    g.client_name = client.client_name
    g.worlds = list(enumerate(worlds))
    g.status = client.status(world=world_number)
    g.users = client.users(world=world_number)
    return render_template("session.html")
