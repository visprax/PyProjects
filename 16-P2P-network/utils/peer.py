"""Peer module. Peer specific functinalities in the P2P network."""

import socket
import logging
import threading

logger = logging.getLogger("peer")

class Peer:
    """Implements the core functionalities of a peer in the network."""

    def __init__(self, maxpeers, nodeport, nodehost = None, nodeid = None):
        """Initialize a node. 

        The node, which is the current peer, keeps info about maxpeers number 
        of other peers, listening on nodeport with the id of nodeid at the nodehost 
        address. If a host address is not given, one will be given by trying to connect 
        to a public internet host, e.g. Google.
        """

        logger.info(f"initializing node:  'maxpeers': {maxpeers}, \
                'port': {nodeport}, 'host': {nodehost}, 'id': {nodeid}")

        self.maxpeers = maxpeers
        self.nodeport = nodeport

        if nodehost:
            self.nodehost = nodehost
        else:
            self._inithost()

        if nodeid:
            self.nodeid = nodeid
        else:
            self._initid()

        self.peerlock = threading.Lock() #? or threading.RLock()?

        # known peers to this node
        self.peers = {} #?
        self.handlers = {}
        # used to break the main node loop
        self.breakloop = False
        self.router = None #?

    def getsocket(self, port, backlog = 5):
        """Prepare a socket for the node to listen on the given port."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # make socket reusable
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # optional backlog param is the number of non-accepted connections allowed to be queued up
        s.listen(backlog)
        return s

    def _inithost(self):
        """If no nodehost were given, determine one by connecting to a public online host."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(("www.google.com", 80))
                self.nodehost = s.getsockname()[0]
                logger.info(f"node host address set to: {self.peerhost}")
            except Exception as err:
                logger.error("node host address couldn't be determined", exc_info=True)

    def _initid(self):
        """If no nodeid were given, set it to 'host:port'"""
        _id = f"{self.nodehost}:{self.nodeport}"
        self.nodeid = _id
        logger.debug(f"nodeid set to {_id}")



