#!/usr/bin/env python3

# NeosVR-Headless-WebUI
# Glitch, 2021

# This server is the interface that allows the web application to connect to and
# communicate with one or more RPC servers and hence multiple headless clients.
# It should be started before the web application is started.

import logging
from threading import Thread
from time import sleep

from rpyc import Service
from neosvr_headless_api import RemoteHeadlessClient

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s",
    level=logging.INFO
)

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
        self.name = name
        self.running = True
        self._info = {}
        self._thread = Thread(target=self._polling_thread)
        self._thread.start()

    def _polling_thread(self):
        # Wait for the headless client to finish starting up.
        self.wait()
        # TODO: This doesn't handle multiple worlds.
        while self.running:
            self._info["worlds"] = super().worlds()
            sleep(1)
            self._info["status"] = super().status()
            sleep(1)
            self._info["users"] = super().users()
            sleep(1)

    # TODO: Block these methods if the client is not ready yet.

    def worlds(self):
        return self._info["worlds"]

    def status(self):
        return self._info["status"]

    def users(self):
        return self._info["users"]

    def shutdown(self):
        self.running = False
        # Wait for polling thread to stop.
        self._thread.join()
        super().shutdown()

class HeadlessClientService(Service):
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.current_id = 0

    def exposed_start_headless_client(self, name, host, port, *args, **kwargs):
        """
        Start a new `HeadlessClientInstance`. Returns a tuple in the form
        of (id, `HeadlessClientInstance`). All arguments and keyword arguments
        are passed to `HeadlessClientInstance` as-is.

        The id can be used to get the `HeadlessClientInstance` again at a
        later time with `get_headless_client()`.

        At the moment, only remote headless clients are supported.
        """
        client = HeadlessClientInstance(name, host, port, *args, **kwargs)
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
        client = self.clients[cid]
        client.shutdown()
        exit_code = client.process.wait()
        del(self.clients[cid])
        logging.info(
            "Headless client with ID %d terminated with return code %d." %
            (cid, exit_code)
        )
        logging.info("Total clients running: %d" % len(self.clients))
        return exit_code

    def exposed_get_headless_client(self, cid):
        """Returns an existing `HeadlessClientInstance` with the given `cid`."""
        return self.clients[cid]

    def exposed_list_headless_clients(self):
        """List all currently running headless clients."""
        # TODO: Ignore clients that are not fully started.
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
            "max_users": 0
        }
        for c in self.clients:
            status["clients"] += 1
            worlds = self.clients[c].worlds()
            status["sessions"] += len(worlds)
            for w in worlds:
                status["current_users"] += w["users"]
                status["present_users"] += w["present"]
                status["max_users"] += w["max_users"]
        return status

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(HeadlessClientService(), port=16882,
        protocol_config={"allow_public_attrs": True} # TODO: Harden this more.
    )
    server.start()
