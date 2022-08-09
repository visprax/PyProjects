#!/usr/bin/env python3

import os
import logging
import argparse
import configparser
from getpass import getpass

# TODO: get username and email from command line
# TODO: email notifications

SUPPORTED_STORE_TYPES = ["db", "json", "yaml"]


def read_file(filepath, filetype):
    pass


def is_valid(username, password):
    return True


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logger = logging.getLogger("xlogin")

    argparser = argparse.ArgumentParser(prog="xlogin", description="Perform dummy login, passsword change, and register")
    argparser.add_argument("command", help="command to perform", choices=["login", "change", "register"])
    argparser.add_argument("--conf", help="path to config file")
    argparser.add_argument('-v', help="print debug messages", action="count")
    args = argparser.parse_args()

    if not args.v:
        logging.disable()
    elif args.v == 1:
        logger.setLevel("ERROR")
    elif args.v == 2:
        logger.setLevel("INFO")
    else:
        logger.setLevel("DEBUG")

    if args.conf:
        config_filepath = args.conf
        if not os.path.isfile(config_filepath):
            logger.critical(f"configuration file '{config_filepath}' doesn't exist.")
            raise SystemExit(f"configuration file '{config_filepath}' doesn't exist.")
    else:
        config_filepath = "login.conf"
        if not os.path.isfile(config_filepath):
            logger.critical(f"configuration file '{config_filepath}' doesn't exist.")
            raise SystemExit(f"configuration file '{config_filepath}' doesn't exist.")


    config = configparser.ConfigParser()
    logger.info("reading configuration file: '{config_filepath}'")
    config.read("login.conf")

    store_type = config["default"]["store_type"]
    if store_type not in SUPPORTED_STORE_TYPES:
        raise SystemExit(f"'store_type': {store_type} in config file not supported.")
    store_path = config["default"]["store_path"]
    if not os.path.exists(store_path):
        raise SystemExit(f"'store_path': {store_path} in config file doesn't exist.")
    store_name = config["default"]["store_name"] + '.' + store_type
    
    passwords_path = store_path + store_name
    if os.path.isfile(passwords_path):
        pfile_exists = True
    else:
        pfile_exists = False
    
    if args.command == "login":
        username = input("username:> ")
        password = getpass("password:> ")

