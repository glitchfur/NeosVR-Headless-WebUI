# NeosVR-Headless-WebUI
# Copyright (C) 2022  GlitchFur

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Blueprint, current_app, jsonify, request, session
from .auth import api_login_required

from rpyc import connect, core

# This is needed to catch exceptions thrown by the internal API.
from neosvr_headless_api import NeosError, HeadlessNotReady

_gec = core.vinegar._generic_exceptions_cache
_gec["neosvr_headless_api.NeosError"] = NeosError
_gec["neosvr_headless_api.HeadlessNotReady"] = HeadlessNotReady

bp = Blueprint("api", __name__, url_prefix="/api/v1")

# TODO: Use different HTTP codes for errors?

# Maximum time to wait for RPC responses (in seconds)
SYNC_REQUEST_TIMEOUT = 60


def connect_manager():
    """Returns an RPC connection to the manager server."""
    return connect(
        current_app.config["MANAGER_HOST"],
        current_app.config["MANAGER_PORT"],
        config={"sync_request_timeout": SYNC_REQUEST_TIMEOUT},
    )


def log_user_action(msg, cmd=None):
    """
    Write an action to the log file, prepending the message with the initiating
    user's username. If `cmd` is specified, it is added to the log message,
    indicating that it was the effective headless client console command ran.
    """
    if cmd:
        return current_app.logger.info(
            "(User: %s, Command: %s) %s" % (session["user"]["username"], cmd, msg)
        )
    else:
        return current_app.logger.info(
            "(User: %s) %s" % (session["user"]["username"], msg)
        )


def start_headless_client(*args, **kwargs):
    conn = connect_manager()
    client = conn.root.start_headless_client(*args, **kwargs)
    return client


def stop_headless_client(client_id):
    conn = connect_manager()
    exit_code = conn.root.stop_headless_client(client_id)
    return exit_code


def get_headless_client(client_id):
    conn = connect_manager()
    client = conn.root.get_headless_client(client_id)
    return client


def list_headless_clients():
    conn = connect_manager()
    clients = conn.root.list_headless_clients()
    status = conn.root.get_manager_status()
    response = {"stats": status, "clients": {}}
    for c in clients:
        # Do not show clients that are not fully started.
        if not clients[c].is_ready():
            continue
        response["clients"][c] = {
            "name": clients[c].client_name,
            "summary": clients[c].summary(),
        }
    return response


def api_response(message):
    """
    Builds and returns an API response, which consists simply of a `success`
    boolean and an accompanying message. If `message` is an exception, "success"
    becomes False and "message" is set as the extracted exception message. If
    `message` is `None`, "success" becomes True and "message" is omitted. If
    `message` is anything other than an exception or `None`, "success" becomes
    True and "message" is set as the message.
    """
    if message == None:
        return {"success": True}
    if isinstance(message, Exception):
        success = False
        message = message.args[0]
    else:
        success = True
    return {"success": success, "message": message}


def convert_netref(obj):
    """
    Recursively converts rpyc's "netref" representation of `dict`s and `list`s
    into native objects. Use this before passing any `dict` or `list` generated
    by an rpyc server directly into Python's standard `json` library, as it does
    not like serializing those objects even though they are supposed to look and
    feel like local objects. If `obj` is neither a `dict` or `list` then `obj`
    is returned without any modification.
    """
    if isinstance(obj, dict):
        res = {}
        for key in obj:
            if isinstance(obj[key], (list, dict)):
                res[key] = convert_netref(obj[key])
            else:
                res[key] = obj[key]
        return res
    elif isinstance(obj, list):
        res = []
        for val in obj:
            if isinstance(val, (list, dict)):
                res.append(convert_netref(val))
            else:
                res.append(val)
        return res
    else:
        return obj


@bp.route("/start", methods=["POST"])
@api_login_required
def start():
    """
    Starts a headless client. Data should be submitted as a URL encoded form.
    Required parameters are `name`, `host`, `port`, and `neos_dir`.
    """
    log_user_action("Initiated headless client start")
    name = request.form["name"]
    host, port = request.form["host"], request.form["port"]
    neos_dir = request.form["neos_dir"]
    config = request.form["config"] if "config" in request.form else None
    cid = start_headless_client(name, host, port, neos_dir, config=config)
    return {"success": True, "client_id": cid[0]}


@bp.route("/list")
@api_login_required
def list_():
    return jsonify(convert_netref(list_headless_clients()))


@bp.route("/find_user", methods=["POST"])
def find_user():
    conn = connect_manager()
    user = request.form["username"]
    found_list = convert_netref(conn.root.find_user(user))
    return {"username": user, "sessions": found_list}


@bp.route("/kick_from_all", methods=["POST"])
def kick_from_all():
    conn = connect_manager()
    user = request.form["username"]
    log_user_action('Initiated kick of user "%s" from all sessions' % user)
    kick_list = convert_netref(conn.root.kick_from_all(user))
    return {"username": user, "kicks": kick_list}


@bp.route("/ban_from_all", methods=["POST"])
def ban_from_all():
    conn = connect_manager()
    user = request.form["username"]
    log_user_action('Initiated ban of user "%s" from all sessions' % user)
    kick = True if request.form["kick"] == "true" else False
    ban_kick_list = convert_netref(conn.root.ban_from_all(user, kick=kick))
    response = {
        "username": user,
        "bans": ban_kick_list["bans"],
        "kicks": ban_kick_list["kicks"],
    }
    return response


@bp.route("/<int:client_id>/sigint", methods=["POST"])
@api_login_required
def sigint(client_id):
    """Send a `SIGINT` signal to the headless client."""
    log_user_action("Initiated SIGINT (2) of headless client with ID %d" % client_id)
    conn = connect_manager()
    # TODO: Implement timeout
    exit_code = conn.root.send_signal_headless_client(client_id, 2)
    return {"success": True, "exit_code": exit_code}


@bp.route("/<int:client_id>/terminate", methods=["POST"])
@api_login_required
def terminate(client_id):
    """Send a `SIGTERM` signal to the headless client."""
    log_user_action("Initiated SIGTERM (15) of headless client with ID %d" % client_id)
    conn = connect_manager()
    # TODO: Implement timeout
    exit_code = conn.root.send_signal_headless_client(client_id, 15)
    return {"success": True, "exit_code": exit_code}


@bp.route("/<int:client_id>/kill", methods=["POST"])
@api_login_required
def kill(client_id):
    """Send a `SIGKILL` signal to the headless client."""
    log_user_action("Initiated SIGKILL (9) of headless client with ID %d" % client_id)
    conn = connect_manager()
    # TODO: Implement timeout
    exit_code = conn.root.send_signal_headless_client(client_id, 9)
    return {"success": True, "exit_code": exit_code}


@bp.route("/<int:client_id>/restart_client", methods=["POST"])
@api_login_required
def restart_client(client_id):
    """
    Attempts to restart a headless client "in-place", by killing the currently
    running one and spawning a new one with the same configuration.
    """
    log_user_action("Restarting headless client with ID %d" % client_id)
    conn = connect_manager()
    client = conn.root.get_headless_client(client_id)
    name = client.client_name
    host = client.host
    port = client.port
    neos_dir = client.neos_dir
    config = client.config
    conn.root.send_signal_headless_client(client_id, 15)
    new_client = conn.root.start_headless_client(
        name, host, port, neos_dir, config=config
    )
    return {"success": True, "client_id": new_client[0]}


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
    log_user_action(
        'Invited user "%s" to client ID %d, session ID %d'
        % (user, client_id, session_id),
        cmd="invite",
    )
    return api_response(response)

@bp.route("/<int:client_id>/friend_requests")
@api_login_required
def friend_requests(client_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.friend_requests()
    except HeadlessNotReady as exc:
        return api_response(exc)
    return convert_netref(response)

@bp.route("/<int:client_id>/accept_friend_request", methods=["POST"])
@api_login_required
def accept_friend_request(client_id):
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.accept_friend_request(user)
    except HeadlessNotReady as exc:
        return api_response(exc)
    log_user_action(
        'Accepted contact request of "%s" from client ID %d'
        % (user, client_id),
        cmd="acceptFriendRequest",
    )
    return api_response(response)


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


@bp.route("/<int:client_id>/<int:session_id>/close", methods=["POST"])
@api_login_required
def close(client_id, session_id):
    """Close the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.close(world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        "Session with ID %d closed on client ID %d" % (session_id, client_id),
        cmd="close",
    )
    return api_response(response)


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
    log_user_action(
        'Kicked user "%s" from client ID %d, session ID %d'
        % (user, client_id, session_id),
        cmd="kick",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/silence", methods=["POST"])
@api_login_required
def silence(client_id, session_id):
    """Silence a user in the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.silence(user, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Silenced user "%s" in client ID %d, session ID %d'
        % (user, client_id, session_id),
        cmd="silence",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/unsilence", methods=["POST"])
@api_login_required
def unsilence(client_id, session_id):
    """Remove silence from a user in the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.unsilence(user, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Unsilenced user "%s" in client ID %d, session ID %d'
        % (user, client_id, session_id),
        cmd="unsilence",
    )
    return api_response(response)


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
    log_user_action(
        'Banned user "%s" in client ID %d, session ID %d'
        % (user, client_id, session_id),
        cmd="ban",
    )
    return api_response(response)


@bp.route("/<int:client_id>/unban", methods=["POST"])
@api_login_required
def unban(client_id):
    """Unbans a given user."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.unban(user)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Unbanned user "%s" from client ID %d' % (user, client_id), cmd="unban"
    )
    return api_response(response)


@bp.route("/<int:client_id>/list_bans")
@api_login_required
def list_bans(client_id):
    """Lists all currently banned users."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    try:
        response = c.list_bans()
    except HeadlessNotReady as exc:
        return api_response(exc)
    return jsonify(response)


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
    log_user_action(
        'Banned user "%s" by name from client ID %d' % (user, client_id),
        cmd="banByName",
    )
    return api_response(response)


@bp.route("/<int:client_id>/unban_by_name", methods=["POST"])
@api_login_required
def unban_by_name(client_id):
    """Unbans a given user by their username."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    try:
        response = c.unban_by_name(user)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Unbanned user "%s" by name from client ID %d' % (user, client_id),
        cmd="unbanByName",
    )
    return api_response(response)


@bp.route("/<int:client_id>/ban_by_id", methods=["POST"])
@api_login_required
def ban_by_id(client_id):
    """Bans a given user by their user ID."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user_id = request.form["id"]
    try:
        response = c.ban_by_id(user_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Banned user ID "%s" from client ID %d' % (user_id, client_id), cmd="banByID"
    )
    return api_response(response)


@bp.route("/<int:client_id>/unban_by_id", methods=["POST"])
@api_login_required
def unban_by_id(client_id):
    """Unbans a given user by their user ID."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user_id = request.form["id"]
    try:
        response = c.unban_by_id(user_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Unbanned user ID "%s" from client ID %d' % (user_id, client_id),
        cmd="unbanByID",
    )
    return api_response(response)


# TODO: Implement `respawn` here


@bp.route("/<int:client_id>/<int:session_id>/role", methods=["POST"])
@api_login_required
def role(client_id, session_id):
    """Change a user's role in the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    user = request.form["username"]
    role = request.form["role"]
    try:
        response = c.role(user, role, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Changed role of "%s" to %s in client ID %d, session ID %d'
        % (user, role, client_id, session_id),
        cmd="role",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/name", methods=["POST"])
@api_login_required
def name(client_id, session_id):
    """Change the name of the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    name = request.form["name"]
    try:
        response = c.name(name, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        'Changed name client ID %d, session ID %d to "%s"'
        % (client_id, session_id, name),
        cmd="name",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/access_level", methods=["POST"])
@api_login_required
def access_level(client_id, session_id):
    """Change the access level of the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    access_level = request.form["access_level"]
    try:
        response = c.access_level(access_level, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        "Changed access level of client ID %d, session ID %d to %s"
        % (client_id, session_id, access_level),
        cmd="accessLevel",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/hide_from_listing", methods=["POST"])
@api_login_required
def hide_from_listing(client_id, session_id):
    """Show or hide the currently focused world from the world listing."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    hide = True if request.form["hide"] == "true" else False
    try:
        response = c.hide_from_listing(hide, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    if hide:
        msg = "hidden from listing"
    else:
        msg = "unhidden from listing"
    log_user_action(
        "Client ID %d, session ID %d %s" % (client_id, session_id, msg),
        cmd="hideFromListing",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/description", methods=["POST"])
@api_login_required
def description(client_id, session_id):
    """Change the description of the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    description = request.form["description"]
    try:
        response = c.description(description, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        "Client ID %d, session ID %d description updated" % (client_id, session_id),
        cmd="description",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/max_users", methods=["POST"])
@api_login_required
def max_users(client_id, session_id):
    """Set the max users allowed in the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    max_users = int(request.form["max_users"])
    try:
        response = c.max_users(max_users, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        "Max users set to %d in client ID %d, session ID %d"
        % (max_users, client_id, session_id),
        cmd="maxUsers",
    )
    return api_response(response)


@bp.route("/<int:client_id>/<int:session_id>/away_kick_interval", methods=["POST"])
@api_login_required
def away_kick_interval(client_id, session_id):
    """Set the away kick interval for the currently focused world."""
    try:
        c = get_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    interval = int(request.form["interval"])
    try:
        response = c.away_kick_interval(interval, world=session_id)
    except (NeosError, HeadlessNotReady) as exc:
        return api_response(exc)
    log_user_action(
        "Away kick interval set to %d in client ID %d, session ID %d"
        % (interval, client_id, session_id),
        cmd="awayKickInterval",
    )
    return api_response(response)


@bp.route("/<int:client_id>/shutdown")
@api_login_required
def shutdown(client_id):
    log_user_action(
        "Initiated shut down of headless client with ID %d" % client_id, cmd="shutdown"
    )
    try:
        exit_code = stop_headless_client(client_id)
    except LookupError as exc:
        return api_response(exc)
    return {"success": True, "exit_code": exit_code}


# TODO: Implement `gc` here
# TODO: Implement `tick_rate` here
