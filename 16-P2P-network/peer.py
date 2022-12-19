"""Peer module. Node specific functinality of the P2P network."""

import socket
import logging
import threading

logger = logging.getLogger("peer")

class Peer:
    """Implements the core functionalities of a peer in the network."""

    def __init__(self, maxpeers, peerport, peerhost = None, peerid = None):
        """Initialize a peer that keeps info about maxpeers number of peers, 
        listening on peerport with the id of peerid at the peerhost address.
        If a host address is not given, one will be given by trying to connect
        to a public internet host, e.g. Google."""

        self.maxpeers = maxpeers
        self.peerport = peerport

        if peerhost:
            self.peerhost = peerhost
        else:
            self.__inithost()

        if peerid:
            self.peerid = peerid
        else:
            self.__initid()

        self.peerlock = threading.Lock()
