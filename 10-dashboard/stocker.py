#!/usr/bin/env python3

import os
import logging
import requests
import argparse
import configparser

from utils.config import Config
from utils.db import Qdb
from utils.worker import Worker

logger = logging.getLogger("stocker")

def get_args():
    argparser = argparse.ArgumentParser(prog="stocker", description="Real-time stocks and cryptocurrency charts")
    argparser.add_argument("--conf", help="path to config file", type=str)
    argparser.add_argument("-v", help="print logging message", action="count")
    args = argparser.parse_args()

    if not args.v:
        log_level = None
    elif args.v == 1:
        log_level = "ERROR"
    elif args.v == 2:
        leg_level == "INFO"
    else:
        log_level = "DEBUG"

    if log_level:
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            logger.setLevel(log_level)
    else:
        logging.disable()
    
    config = configparser.ConfigParser()
    if not args.conf:
        args.conf = "stocker.conf"
    if not os.path.exists(args.conf):
        logger.error(f"config file doesn't exists at: {args.conf}")
        raise SystemExit()
    
    param_config = Config(args.conf)
    params = param_config.get_config()

    return params

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)
    
    params = get_args()
     
    db = Qdb(params)
    result = db.create_table()

    worker = Worker(params)
    app = worker.celery
    app.worker_main(["worker", "--beat", "-c 1"])
