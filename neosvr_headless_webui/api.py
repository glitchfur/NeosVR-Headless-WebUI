from flask import Blueprint, current_app, jsonify, request
from .auth import api_login_required

from rpyc import connect

bp = Blueprint("api", __name__, url_prefix="/api/v1")

# TODO: Throw 404 on commands that execute on users if the user wasn't found.

def start_headless_client(*args, **kwargs):
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    client = conn.root.start_headless_client(*args, **kwargs)
    return client

def stop_headless_client(client_id):
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    exit_code = conn.root.stop_headless_client(client_id)
    return exit_code

def get_headless_client(client_id):
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    client = conn.root.get_headless_client(client_id)
    return client

def list_headless_clients():
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    clients = conn.root.list_headless_clients()
    status = conn.root.get_manager_status()
    response = {
        "stats": status,
        "clients": {}
    }
    for c in clients:
        response["clients"][c] = {
            "name": clients[c].name,
            "summary": clients[c].summary()
        }
    return response

@bp.route("/start", methods=["POST"])
@api_login_required
def start():
    """
    Starts a headless client. Data should be submitted as a URL encoded form.
    Required parameters are `name`, `host`, `port`, and `neos_dir`.
    """
    name = request.form["name"]
    host, port = request.form["host"], request.form["port"]
    neos_dir = request.form["neos_dir"]
    cid = start_headless_client(name, host, port, neos_dir)
    return {"success": True, "client_id": cid[0]}

@bp.route("/list")
@api_login_required
def list_clients():
    return jsonify(list_headless_clients())

# TODO: Implement `login` here
# TODO: Implement `logout` here

@bp.route("/<int:client_id>/message", methods=["POST"])
@api_login_required
def message(client_id):
    c = get_headless_client(client_id)
    user, msg = request.form["username"], request.form["message"]
    response = c.message(user, msg)
    return response

@bp.route("/<int:client_id>/<int:session_id>/invite", methods=["POST"])
@api_login_required
def invite(client_id, session_id):
    c = get_headless_client(client_id)
    user = request.form["username"]
    response = c.invite(user, world=session_id)
    return response

# TODO: Implement `friend_requests` here
# TODO: Implement `accept_friend_request` here

@bp.route("/<int:client_id>/worlds")
@api_login_required
def worlds(client_id):
    c = get_headless_client(client_id)
    return jsonify(c.worlds())

# TODO: Implement `focus` here

# TODO: Implement `start_world_url` here
# TODO: Implement `start_world_template` here

@bp.route("/<int:client_id>/<int:session_id>/status")
@api_login_required
def status(client_id, session_id):
    c = get_headless_client(client_id)
    return jsonify(c.status(session_id))

@bp.route("/<int:client_id>/<int:session_id>/session_url")
@api_login_required
def session_url(client_id, session_id):
    c = get_headless_client(client_id)
    return c.session_url(world=session_id)

@bp.route("/<int:client_id>/<int:world_number>/session_id")
@api_login_required
def session_id(client_id, world_number):
    c = get_headless_client(client_id)
    return c.session_id(world=world_number)

@bp.route("/<int:client_id>/<int:session_id>/users")
@api_login_required
def users(client_id, session_id):
    c = get_headless_client(client_id)
    return jsonify(c.users(session_id))

# TODO: Implement `close` here
# TODO: Implement `save` here
# TODO: Implement `restart` here

@bp.route("/<int:client_id>/<int:session_id>/kick", methods=["POST"])
@api_login_required
def kick(client_id, session_id):
    """Kicks a given user from the currently focused world."""
    c = get_headless_client(client_id)
    user = request.form["username"]
    response = c.kick(user, world=session_id)
    return response

# TODO: Implement `silence` here
# TODO: Implement `unsilence` here

@bp.route("/<int:client_id>/<int:session_id>/ban", methods=["POST"])
@api_login_required
def ban(client_id, session_id):
    """Bans a given user from the currently focused world."""
    c = get_headless_client(client_id)
    user = request.form["username"]
    response = c.ban(user, world=session_id)
    return response

# TODO: Implement `unban` here

@bp.route("/<int:client_id>/ban_by_name", methods=["POST"])
@api_login_required
def ban_by_name(client_id):
    """Bans a given user by their username."""
    c = get_headless_client(client_id)
    user = request.form["username"]
    response = c.ban_by_name(user)
    return response

# TODO: Implement `unban_by_name` here
# TODO: Implement `ban_by_id` here
# TODO: Implement `unban_by_id` here
# TODO: Implement `respawn` here
# TODO: Implement `role` here
# TODO: Implement `name` here
# TODO: Implement `access_level` here
# TODO: Implement `hide_from_listing` here
# TODO: Implement `description` here
# TODO: Implement `max_users` here
# TODO: Implement `away_kick_interval` here

@bp.route("/<int:client_id>/shutdown")
@api_login_required
def shutdown(client_id):
    exit_code = stop_headless_client(client_id)
    return {"success": True, "exit_code": exit_code}

# TODO: Implement `gc` here
# TODO: Implement `tick_rate` here
