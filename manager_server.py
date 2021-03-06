#!/usr/bin/env python3

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

"""
This server is the interface that allows the web application to connect to and
communicate with one or more RPC servers and hence multiple headless clients.
It should be started before the web application is started.
"""

import logging
import argparse
from threading import Thread
from json import load
from time import time, sleep

from rpyc import Service
from neosvr_headless_api import RemoteHeadlessClient, NeosError, HeadlessNotReady

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s", level=logging.INFO
)

NOT_READY_MESSAGE = "The headless client is not ready yet. Try again soon."


def main():
    parser = argparse.ArgumentParser(
        description="Manage multiple NeosVR-Headless-API RPC servers"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="The host or IP address to bind to. (Default: 127.0.0.1)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=16882,
        help="The TCP port to bind to. (Default: 16882)",
    )
    parser.add_argument("-a", "--autostart", help="Path to autostart JSON file.")
    args = parser.parse_args()

    if args.autostart:
        with open(args.autostart) as fp:
            autostart = load(fp)
    else:
        autostart = None

    from rpyc.utils.server import ThreadedServer

    server = ThreadedServer(
        HeadlessClientService(autostart=autostart),
        hostname=args.host,
        port=args.port,
        protocol_config={
            # TODO: Harden this more.
            "allow_public_attrs": True,
            # I'm not sure if this is needed or not, nor do I know what it does,
            # but it's in the example documentation so it's going here.
            "import_custom_exceptions": True,
        },
    )
    server.start()


class HeadlessClientInstance(RemoteHeadlessClient):
    """
    This is a small wrapper around the `HeadlessClient` class, but an important
    one. It makes command I/O more performant in the context of a multi-user
    application such as this one.

    Under no load, the headless client typically processes commands immediately.
    However, under heavy load, commands can sometimes experience substantial
    delays. Some "read-only" commands like "worlds", "status", and "users" need
    to be run often, yet will contain little to no changes from the previous
    run. This is where this class comes in.

    This class will "poll" those commands at regular intervals and cache their
    results. Executing the methods for these commands will pull from this cache
    rather execute the commands directly. This way, the output is returned
    immediately, at the cost of the information being potentially outdated by a
    few seconds. In the long run it should keep page load times from being
    disastrously high when headless clients are under heavy load.

    It also tacks on other attributes such as "name" for easier identification
    of headless clients in the web interface.

    At the moment, only remote headless clients are supported.
    """

    def __init__(self, name, host, port, *args, **kwargs):
        super().__init__(host, port, *args, **kwargs)
        # The name of the headless client itself, not any session.
        self.client_name = name
        self.start_time = time()
        # The last time that the cache for `worlds`, `status`, and `users` was
        # fully updated. The polling thread continuously updates this value. If
        # it lags too far behind the current time, it could be an indicator that
        # the headless client is frozen or died.
        self.last_update = time()
        self.running = True
        # The keys of the "status" and "users" dicts will be world numbers, or
        # sessions. The values of these will again be dicts of that world's
        # respective status and list of users.
        self._info = {"status": {}, "users": {}, "session_id": {}, "session_url": {}}
        self._polling_thread = Thread(target=self._polling_thread)
        self._polling_thread.start()

    def _polling_thread(self):
        # Wait for the headless client to finish starting up. This is looped so
        # that it doesn't block indefinitely and allows for a chance to abort in
        # case the headless client never fully starts.
        while self.running:
            ready = self.wait_for_ready(timeout=0.5)
            if ready:
                break
        while self.running:
            # "worlds" command has the scope of the whole headless client and
            # doesn't need to be run per world.
            self._info["worlds"] = super().worlds()
            # Clean up the "status" and "users" `dict`s by removing keys for
            # worlds that no longer exist. Admittedly funky way of doing it,
            # because "worlds" is a `list`, not a `dict`.
            world_indexes = set(range(len(self._info["worlds"])))
            for d in ("status", "users", "session_id", "session_url"):
                remove = set(self._info[d]).difference(world_indexes)
                for i in remove:
                    del self._info[d][i]
            sleep(0.5)
            # "status" and "users" have the scope of a single session and so
            # need to be run per session.
            for i in world_indexes:
                try:
                    status = super().status(world=i)
                    self._info["status"][i] = status
                    # Session IDs don't change, no need to update over and over.
                    if not i in self._info["session_id"]:
                        self._info["session_id"][i] = status["session_id"]
                    sleep(0.5)
                    self._info["users"][i] = super().users(world=i)
                    sleep(0.5)
                    # Same comment as above, but for session URLs.
                    if not i in self._info["session_url"]:
                        self._info["session_url"][i] = super().session_url(world=i)
                        sleep(0.5)
                except NeosError:
                    # If we got here, a world was closed after we called
                    # `worlds()`. Don't bother running the rest of the loop
                    # (because the index of the worlds after will have shifted)
                    # and call `worlds()` again.
                    break
            # Update the last time this loop completed successfully.
            self.last_update = time()

    def get_state(self):
        """
        Get the current "state" of the headless client as a tuple, consisting of
        two parts: A string, and a number of seconds. There are four possible
        values:

        * ("starting", <int>) - The headless client is starting, and <int> is
          the number of seconds the client has been starting for.
        * ("stuck_starting", <int>) - The headless client has been starting for
          over a minute and may be stuck. <int> is the number of seconds the
          client has been starting for.
        * ("running", <int>) - The headless client is running normally and is
          ready to accept commands. <int> is the number of seconds the client
          has been running for.
        * ("not_responding", <int>) - The headless client hasn't completed its
          polling loop for over 45 seconds. <int> is the number of seconds since
          the last time the loop completed a full cycle.
        """
        ct = time()
        if not self.is_ready():
            sd = int(ct - self.start_time)
            if sd > 60:
                return ("stuck_starting", sd)
            return ("starting", sd)
        ud = int(ct - self.last_update)
        if ud > 45:
            return ("not_responding", ud)
        return ("running", ct - self.start_time)

    # TODO: Check whether these are completely empty. This should only occur
    # during the brief period of time between the headless client being ready
    # and these being polled for the first time.

    # TODO: Eliminate some redundancy here.

    def worlds(self):
        if not self.is_ready():
            raise HeadlessNotReady(NOT_READY_MESSAGE)
        return self._info["worlds"]

    def status(self, world):
        if not self.is_ready():
            raise HeadlessNotReady(NOT_READY_MESSAGE)
        if not world in self._info["status"]:
            raise LookupError("No session with ID %d" % world)
        return self._info["status"][world]

    def users(self, world):
        if not self.is_ready():
            raise HeadlessNotReady(NOT_READY_MESSAGE)
        if not world in self._info["users"]:
            raise LookupError("No session with ID %d" % world)
        return self._info["users"][world]

    def session_id(self, world):
        if not self.is_ready():
            raise HeadlessNotReady(NOT_READY_MESSAGE)
        if not world in self._info["session_id"]:
            raise LookupError("No session with ID %d" % world)
        return self._info["session_id"][world]

    def session_url(self, world):
        if not self.is_ready():
            raise HeadlessNotReady(NOT_READY_MESSAGE)
        if not world in self._info["session_url"]:
            raise LookupError("No session with ID %d" % world)
        return self._info["session_url"][world]

    def summary(self):
        """
        Return cumulative stats of all currently running sessions.
        This is not a built-in headless client command.
        """
        # TODO: Maybe check if the client is ready here instead of relying
        # on the `worlds()` call to fail. It doesn't affect anything though ...
        status = {"sessions": 0, "current_users": 0, "present_users": 0, "max_users": 0}
        worlds = self.worlds()
        status["sessions"] += len(worlds)
        for w in worlds:
            status["current_users"] += w["users"]
            status["present_users"] += w["present"]
            status["max_users"] += w["max_users"]
        return status

    def shutdown(self):
        self.running = False
        # Wait for polling thread to stop.
        self._polling_thread.join()
        super().shutdown()


class HeadlessClientService(Service):
    def __init__(self, autostart=None):
        super().__init__()
        self.clients = {}
        self.current_id = 0

        def autostart_thread():
            for c in autostart:
                client = self.exposed_start_headless_client(
                    c["name"], c["host"], c["port"], c["neos_dir"], c["config"]
                )
                # Start each headless client immediately after the previous one
                # is ready, or wait up to 30 seconds. Whichever comes first.
                client[1].wait_for_ready(timeout=30)

        if autostart:
            _autostart_thread = Thread(target=autostart_thread)
            _autostart_thread.start()

    def exposed_start_headless_client(self, name, host, port, *args, **kwargs):
        """
        Start a new `HeadlessClientInstance`. Returns a tuple in the form
        of (id, `HeadlessClientInstance`). All arguments and keyword arguments
        are passed to `HeadlessClientInstance` as-is.

        The id can be used to get the `HeadlessClientInstance` again at a
        later time with `get_headless_client()`.

        At the moment, only remote headless clients are supported.
        """
        for i in range(1, 61):
            try:
                logging.info("Trying connection to %s (%d/60) ..." % (host, i))
                client = HeadlessClientInstance(name, host, port, *args, **kwargs)
                break
            except ConnectionRefusedError:
                sleep(5)
        else:
            raise ConnectionRefusedError

        self.current_id += 1
        self.clients[self.current_id] = client
        logging.info("Starting headless client with ID: %d" % self.current_id)
        logging.info("Neos Dir: %s" % client.neos_dir)
        logging.info("Config: %s" % client.config)
        logging.info("Total clients running: %d" % len(self.clients))
        return (self.current_id, client)

    def exposed_stop_headless_client(self, cid):
        """
        Stops the `HeadlessClientInstance` with the given `cid` and removes it
        from the client list. Returns the exit code of the client.
        """
        if not cid in self.clients:
            raise LookupError("No headless client with ID %d" % cid)
        client = self.clients[cid]
        client.shutdown()
        exit_code = client.process.wait()
        del self.clients[cid]
        logging.info(
            "Headless client with ID %d terminated with return code %d."
            % (cid, exit_code)
        )
        logging.info("Total clients running: %d" % len(self.clients))
        return exit_code

    def exposed_send_signal_headless_client(self, cid, sig):
        """
        Send a signal to the `HeadlessClientInstance` with the given `cid` and
        removes it from the client list. `sig` is an integer which can be either
        SIGINT (2), SIGTERM (15), or SIGKILL (9). If `sig` is not one of these
        integers, `ValueError` will be raised. Returns the signal used to
        terminate the client as a negative integer.
        """
        if not cid in self.clients:
            raise LookupError("No headless client with ID %d" % cid)
        client = self.clients[cid]
        client.running = False
        # Wait for polling thread to stop.
        client._polling_thread.join()
        if not sig in (2, 9, 15):
            # TODO: Handle this
            raise ValueError("Signal not allowed: %d" % sig)
        if sig == 2:
            func = client.sigint
        elif sig == 9:
            func = client.kill
        elif sig == 15:
            func = client.terminate
        exit_code = func()
        # TODO: The following code is identical to that of
        # `exposed_stop_headless_client()`
        del self.clients[cid]
        logging.info(
            "Headless client with ID %d terminated with return code %d."
            % (cid, exit_code)
        )
        logging.info("Total clients running: %d" % len(self.clients))
        return exit_code

    def exposed_get_headless_client(self, cid):
        """Returns an existing `HeadlessClientInstance` with the given `cid`."""
        if not cid in self.clients:
            raise LookupError("No headless client with ID %d" % cid)
        return self.clients[cid]

    def exposed_list_headless_clients(self):
        """List all currently running headless clients."""
        return self.clients

    def exposed_get_manager_status(self):
        """
        Get the current status of the headless client manager, including the
        number of clients and sessions currently running, the number of
        connected and present users, and the cumulative max user limit.
        """
        status = {
            "clients": 0,
            "sessions": 0,
            "current_users": 0,
            "present_users": 0,
            "max_users": 0,
        }
        for c in self.clients:
            # Skip clients that are still starting up.
            if not self.clients[c].is_ready():
                continue
            status["clients"] += 1
            summary = self.clients[c].summary()
            names = ("sessions", "current_users", "present_users", "max_users")
            for n in names:
                status[n] += summary[n]
        return status

    def exposed_find_user(self, username):
        """
        Search for the given username in all sessions, on all headless clients.
        Returns a list of sessions they're currently connected to (NOT including
        present worlds), and a list of sessions they're actually present in.
        The search is case-insensitive.

        The specific format for the returned value (a `dict`) is as follows:

        {
            "current": [(client_id, session_id)],
            "present": [(client_id, session_id)]
        }

        The "current" and "present" keys are both a `list` of `tuple`s
        consisting of both a `client_id` where the user was found, and the
        `session_id` they are in. `session_id` is the same as the world number,
        as shown by the `worlds` command in the headless client.

        While Neos users cannot be present in more than one world at once, the
        "present" `list` may contain more than one `tuple` if the user had just
        switched sessions and the information in both sessions had not yet
        updated to reflect this. It's up to the caller to decide what to do with
        this information.

        If the user is not connected to any headless clients at all, both of
        these `list`s should be empty.
        """
        response = {"current": [], "present": []}
        for cid in self.clients:
            # Skip clients that are still starting up.
            if not self.clients[cid].is_ready():
                continue
            for sid, w in enumerate(self.clients[cid].worlds()):
                for u in self.clients[cid].users(sid):
                    if u["name"].lower() == username.lower():
                        if u["present"]:
                            response["present"].append((cid, sid))
                        else:
                            response["current"].append((cid, sid))
                        break
        return response

    def exposed_kick_from_all(self, username):
        """
        Attempt to kick the given username from all sessions, on all headless
        clients. If the user exists in a session, they will be kicked. If not,
        the command fails silently. Returns a `list` of clients and sessions
        they were kicked from, in the format of `[(client_id, session_id)]`.
        """

        # Kicks are performed asynchronously on all headless clients.

        asyncs, kicks = [], []
        for cid in self.clients:
            # Skip clients that are still starting up.
            if not self.clients[cid].is_ready():
                continue
            for sid, w in enumerate(self.clients[cid].worlds()):
                asyncs.append(
                    (
                        cid,
                        sid,
                        self.clients[cid].async_(
                            self.clients[cid].kick, username, world=sid
                        ),
                    )
                )
        for k in asyncs:
            # TODO: Better exception handling?
            if k[2].exception() == None:
                kicks.append((k[0], k[1]))
        return kicks

    def exposed_ban_from_all(self, username, kick=False):
        """
        Attempt to ban the given username from all headless clients. Optionally,
        also attempt to kick the user from all sessions. Bans apply at the
        headless client level, meaning they restrict access to all sessions
        hosted by a single client. Users cannot be banned per session.

        Returns a `dict` with two keys: "bans", and "kicks". "bans" is a `list`
        of client IDs, whereas "kicks" is a `list` of `tuple`s, containing both
        client and session IDs in the format: `(client_id, session_id)`.

        "bans" should almost always be a list of all headless clients currently
        running, or an empty list. A filled list indicates the ban was
        successful. An empty list indicates the username was not found and no
        ban occurred, or there are no clients running.

        "kicks" will only be populated if `kick` is set to `True`, and it
        represents the clients and sessions that the user was kicked from, if
        any. Otherwise, "kicks" will be an empty list.

        `kick` is `False` by default because the `banByName` and `banByID`
        commands in the headless client do not kick users by themselves. Setting
        `kick` to `True` will perform a separate kick operations after the bans.
        """

        # Bans/kicks are performed asynchronously on all headless clients.

        async_bans, async_kicks, bans, kicks = [], [], [], []
        for cid in self.clients:
            # Skip clients that are still starting up.
            if not self.clients[cid].is_ready():
                continue
            async_bans.append(
                (cid, self.clients[cid].async_(self.clients[cid].ban_by_name, username))
            )
            if kick:
                for sid, w in enumerate(self.clients[cid].worlds()):
                    async_kicks.append(
                        (
                            cid,
                            sid,
                            self.clients[cid].async_(
                                self.clients[cid].kick, username, world=sid
                            ),
                        )
                    )
        for b in async_bans:
            # TODO: Better exception handling?
            if b[1].exception() == None:
                bans.append(b[0])
        for k in async_kicks:
            # TODO: Better exception handling?
            if k[2].exception() == None:
                kicks.append((k[0], k[1]))
        return {"bans": bans, "kicks": kicks}


if __name__ == "__main__":
    main()
