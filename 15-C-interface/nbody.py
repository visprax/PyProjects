#!/usr/bin/env python3

import logging
import argparse

from utils.wrapper import Params, Particle, Solver


logger = logging.getLogger("nbody")

def main():
    pass

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')

    argparser = argparse.ArgumentParser(prog="nbody", \
            description="Solve gravitational NBody problem using a Leap-frog integration scheme.")
    argparser.add_argument("-v", help="control verbosity of the output including debugging messages", action="count")
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

