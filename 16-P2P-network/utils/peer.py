"""Peer module. Node specific functinalities of the P2P network."""

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

        logger.info(f"initializing peer:  'maxpeers': {maxpeers}, 'port': {peerport}, 'host': {peerhost}, 'id': {peerid}")

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

        self.peerlock = threading.Lock() #? or threading.RLock()?

        # known peers to this node
        self.peers = {} #?
        self.handlers = {}
        # used to break the main peer loop
        self.breakloop = False
        self.router = None #?


    def __inithost(self):
        """If no peerhost were given, determine one by connecting to a public online host."""
        pass

    def __initid(self):
        """If no peerid were given, set it to 'peerhost:peerport'"""
        self.peerid = f"{self.peerhost}:{self.peerport}"



