from flask import Blueprint, current_app, g, render_template
from .auth import login_required

from rpyc import connect

bp = Blueprint("client", __name__, url_prefix="/client")

@bp.route("/<int:client_id>")
@login_required
def get_client(client_id):
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    try:
        client = conn.root.get_headless_client(client_id)
    except KeyError:
        return ("This client does not exist.", 404) # TODO: Pretty 404
    g.client_id = client_id
    g.name = client.name
    g.status = client.status()
    g.users = client.users()
    return render_template("client.html")
