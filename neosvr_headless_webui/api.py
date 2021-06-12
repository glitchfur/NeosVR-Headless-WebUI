from flask import Blueprint, current_app, jsonify, request
from .auth import api_login_required

from rpyc import connect, core

# This is needed to catch exceptions thrown by the internal API.
from neosvr_headless_api import NeosError, HeadlessNotReady
_gec = core.vinegar._generic_exceptions_cache
_gec["neosvr_headless_api.NeosError"] = NeosError
_gec["neosvr_headless_api.HeadlessNotReady"] = HeadlessNotReady

bp = Blueprint("api", __name__, url_prefix="/api/v1")

# TODO: Use different HTTP codes for errors?

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
        # Do not show clients that are not fully started.
        if not clients[c].ready.is_set():
            continue
        response["clients"][c] = {
            "name": clients[c].name,
            "summary": clients[c].summary()
        }
    return response

def api_response(message):
    """
    Builds and returns an API response, which consists simply of a `success`
    boolean and an accompanying message. If `message` is an exception, "success"
    becomes False and "message" is set as the extracted exception message. If
    `message` is anything other than an exception, "success" becomes True and
    "message" is set as the message.
    """
    if isinstance(message, Exception):
        success = False
        message = message.args[0]
    else:
        success = True
    return {"success": success, "message": message}

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
def list_():
    return jsonify(list_headless_clients())

@bp.route("/find_user", methods=["POST"])
def find_user():
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    user = request.form["username"]
    found_list = conn.root.find_user(user)
    return {"username": user, "sessions": found_list}

@bp.route("/kick_from_all", methods=["POST"])
def kick_from_all():
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    user = request.form["username"]
    kick_list = conn.root.kick_from_all(user)
    return {"username": user, "kicks": kick_list}

@bp.route("/ban_from_all", methods=["POST"])
def ban_from_all():
    conn = connect(
        current_app.config["MANAGER_HOST"], current_app.config["MANAGER_PORT"]
    )
    user = request.form["username"]
    kick = True if request.form["kick"] == "true" else False
    ban_kick_list = conn.root.ban_from_all(user, kick=kick)
    response = {
        "username": user,
        "bans": ban_kick_list["bans"],
        "kicks": ban_kick_list["kicks"]
    }
    return response

# START HEADLESS COMMANDS

# TODO: Implement `login` here
# TODO: Implement `logout` here

@bp.route("/<int:client_id>/message", methods=["POST"])
@api_login_required
def message(client_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user, msg = request.form["username"], request.form["message"]
    try:
        response = c.message(user, msg)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return api_response(response)

@bp.route("/<int:client_id>/<int:session_id>/invite", methods=["POST"])
@api_login_required
def invite(client_id, session_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.invite(user, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return api_response(response)

# TODO: Implement `friend_requests` here
# TODO: Implement `accept_friend_request` here

@bp.route("/<int:client_id>/worlds")
@api_login_required
def worlds(client_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.worlds()
    except HeadlessNotReady as exc:
        return api_response(exc)
    return jsonify(response)

# TODO: Implement `focus` here

# TODO: Implement `start_world_url` here
# TODO: Implement `start_world_template` here

@bp.route("/<int:client_id>/<int:session_id>/status")
@api_login_required
def status(client_id, session_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.status(session_id)
    except (HeadlessNotReady, LookupError) as exc:
        return api_response(exc)
    return jsonify(response)

@bp.route("/<int:client_id>/<int:session_id>/session_url")
@api_login_required
def session_url(client_id, session_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.session_url(world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return response

@bp.route("/<int:client_id>/<int:world_number>/session_id")
@api_login_required
def session_id(client_id, world_number):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.session_id(world=world_number)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return response

@bp.route("/<int:client_id>/<int:session_id>/users")
@api_login_required
def users(client_id, session_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.users(session_id)
    except (HeadlessNotReady, LookupError) as exc:
        return api_response(exc)
    return jsonify(response)

# TODO: Implement `close` here
# TODO: Implement `save` here
# TODO: Implement `restart` here

@bp.route("/<int:client_id>/<int:session_id>/kick", methods=["POST"])
@api_login_required
def kick(client_id, session_id):
    """Kicks a given user from the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.kick(user, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return api_response(response)

# TODO: Implement `silence` here
# TODO: Implement `unsilence` here

@bp.route("/<int:client_id>/<int:session_id>/ban", methods=["POST"])
@api_login_required
def ban(client_id, session_id):
    """Bans a given user from the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.ban(user, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return api_response(response)

# TODO: Implement `unban` here

@bp.route("/<int:client_id>/ban_by_name", methods=["POST"])
@api_login_required
def ban_by_name(client_id):
    """Bans a given user by their username."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.ban_by_name(user)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    return api_response(response)

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
    try:
        exit_code = stop_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    return {"success": True, "exit_code": exit_code}

# TODO: Implement `gc` here
# TODO: Implement `tick_rate` here
