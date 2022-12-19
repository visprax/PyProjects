#!/usr/bin/env python

import logging
import argparse

from utils.peer import Peer

logger = logging.getLogger("p2p")

def test_network():
    peer = Peer(5, 65500, "192.168.10.0", "10")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    argparser = argparse.ArgumentParser(prog="p2p", description="A Peer-to-Peer network framework")
    argparser.add_argument('-v', help="control logging output level", action="count")
    args = argparser.parse_args()

    if not args.v:
        log_level = None
    elif args.v == 1:
        log_level = "ERROR"
    elif args.v == 2:
        log_level = "INFO"
    else:
        log_level = "DEBUG"

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    if not log_level:
        logging.disable()
    else:
        for logger in loggers:
            logger.setLevel(log_level)


    test_network()
