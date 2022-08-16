#!/usr/bin/env python3

import logging
import requests
import argparse
import configparser

from utils.db import questdb_create_table

logger = logging.getLogger("stocker")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)

    argparser = argparse.ArgumentParser(prog="stocker", description="Real-time stocks and cryptocurrency charts")
    argparser.add_argument("--conf", help="path to config file")
    argparser.add_argument("-v", help="print logging message", action="count")
    if not args.v:
        logging.disable()
    elif args.v == 1:
        log_level = "ERROR"
    elif args.v == 2:
        leg_level == "INFO"
    else:
        log_level = "DEBUG"
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(log_level)
    
    logger.info("reading config file")
    config = configparser.ConfigParser()
    if args.conf:
        conf.read(args.conf)
    else:
        conf.read("app.conf")

    result = questdb_create_table()

    print(result)
