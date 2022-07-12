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
