#!/usr/bin/env python3

import os
import json
import yaml
import sqlite3
import logging
import hashlib
import argparse
import configparser
from getpass import getpass

# TODO: get username and email from command line
# TODO: email notifications



def get_hash(string):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()

def change_password(username, password, store_type, passwords_path):
    pass

def is_valid(username, password, store_type, passwords_path):
    if not os.path.isfile(passwords_path):
        logger.critical(f"passwords database file '{passwords_path}' doesn't exist")
        raise SystemExit()

    logger.info(f"checking validity of username: {username} against provided password")
    if store_type in ["yaml", "json"]:
        if store_type == "yaml":
            logger.debug(f"reading yaml passwords file: '{passwords_path}'")
            with open(passwords_path, 'r') as yamlfile:
                data = yaml.safe_load(yamlfile)
        else:
            logger.debug(f"reading json passwords file: '{passwords_path}'")
            with open(passwords_path, 'r') as jsonfile:
                data = json.load(jsonfile)
        generator = (item for item in data if item["username"]==username)
        # if the username is in data return that entry else return false
        entry = next(generator, False)
        if entry:
            if entry["password_hash"] == get_hash(password):
                return True
            else:
                return False
        return entry
    
    else:
        logger.debug(f"querying passwords database: '{passwords_path}'")
        conn = sqlite3.connect()
        c = conn.cursor()
        query = "SELECT * FROM users WHERE username = ? AND passwords_hash = ?"
        entry = c.execute(query, (username, get_hash(password))).fetchone()
        return entry is not None


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
            logger.critical(f"config file '{config_filepath}' doesn't exist")
            raise SystemExit()
    else:
        config_filepath = "login.conf"
        if not os.path.isfile(config_filepath):
            logger.critical(f"config file '{config_filepath}' doesn't exist")
            raise SystemExit()

    config = configparser.ConfigParser()
    logger.info(f"reading config file: '{config_filepath}'")
    config.read(config_filepath)

    store_type = config["default"]["store_type"]
    supported_store_types = ["db", "json", "yaml"]
    if store_type not in supported_store_types:
        logger.critical(f"'store_type': {store_type} in config file not supported")
        raise SystemExit()
    store_path = config["default"]["store_path"]
    if not os.path.exists(store_path):
        logger.critical(f"'store_path': {store_path} in config file doesn't exist")
        raise SystemExit()
    store_name = config["default"]["store_name"] + '.' + store_type
    
    passwords_path = os.path.join(store_path, store_name)
    
    if args.command == "login":
        username = input("username:> ")
        password = getpass("password:> ")

        logger.info(f"attempting to login with username: '{username}'")
        if is_valid(username, password, store_type, passwords_path):
            print("Login successful.")
        else:
            print("Access denied.")

    if args.command == "change":
        username = input("username:> ")
        password = getpass("old password:> ")
        if is_valid(username, password, store_type, passwords_path):
            logger.info(f"attempting to change password for username: '{username}'")
            # 3 tries for changing password in case the two don't match
            tries = 0
            while tries < 3:
                tries += 1
                password1 = getpass("new password:> ")
                password2 = getpass("confirm password:> ")
                if password1 == password2:
                    change_password(username, password1, store_type, passwords_path)
                    break
                else:
                    print("Passwords don't match.")
            if tries == 3:
                logger.error("maximum tries for changing password is reached, try again.")
                print("Try again later.")
                raise SystemExit()
        else:
            logger.error(f"username: '{username}' and password doesn't match an entry.")
            print("Username or Password doesn't exist.")
            raise SystemExit()

