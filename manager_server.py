#!/usr/bin/env python3

# NeosVR-Headless-WebUI
# Glitch, 2021

# This server is the interface that allows the web application to connect to and
# communicate with one or more RPC servers and hence multiple headless clients.
# It should be started before the web application is started.

import logging

from rpyc import Service
from neosvr_headless_api import RemoteHeadlessClient

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(message)s",
    level=logging.INFO
)

class HeadlessClientService(Service):
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.current_id = 0

    def exposed_start_headless_client(self, *args, **kwargs):
        """
        Start a new instance of a `HeadlessClient`. Returns a tuple in the form
        of (id, `HeadlessClient` instance). All arguments and keyword arguments
        are passed to `HeadlessClient` as-is.

        The id can be used to get the `HeadlessClient` instance again at a
        later time with `get_headless_client()`.

        At the moment, only remote headless clients are supported, so `host` and
        `port` arguments must be provided as per that class's argument list.
        """
        client = RemoteHeadlessClient(*args, **kwargs)
        self.current_id += 1
        self.clients[self.current_id] = client
        logging.info("Starting headless client with ID: %d" % self.current_id)
        logging.info("Neos Dir: %s" % client.neos_dir)
        logging.info("Config: %s" % client.config)
        logging.info("Total clients running: %d" % len(self.clients))
        return (self.current_id, client)

    def exposed_stop_headless_client(self, cid):
        """
        Stops the `HeadlessClient` with the given `cid` and removes it from the
        client list. Returns the exit code of the client.
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
        """Returns an existing `HeadlessClient` with the given `cid`."""
        return self.clients[cid]

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(HeadlessClientService(), port=16882,
        protocol_config={"allow_public_attrs": True} # TODO: Harden this more.
    )
    server.start()
