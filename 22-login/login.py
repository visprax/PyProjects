#!/usr/bin/env python3

import os
import configparser
from getpass import getpass

SUPPORTED_STORE_TYPES = ["db", "json", "yaml"]
SUPPORTED_COMMANDS = ["/login", "/change", "/register"]

def read_file(filepath, filetype):
    if filetype == "yaml":



def is_valid(username, password):
    return True


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("login.conf")

    store_type = config["default"]["store_type"]
    if store_type not in SUPPORTED_STORE_TYPES:
        raise SystemExit(f"'store_type': {store_type} in config file not supported.")
    store_path = config["default"]["store_path"]
    if not os.path.exists(store_path):
        raise SystemExit(f"'store_path': {store_path} in config file doesn't exist.")
    store_name = config["default"]["store_name"] + '.' + store_type
    
    filepath = store_path + store_name
    if os.path.isfile(filepath):
        pfile_exists = True
    else:
        pfile_exists = False
    
    print("Command could be one of '/login', '/change', or '/register'")
    command = input("command:> ")
    if command not in SUPPORTED_COMMANDS:
        raise SystemExit(f"'command': {command} is not supported.")
    
    if command == "/login" and not pfile_exists:
        raise SystemExit(f"'password file': {filepath} doesn't exists, can't login.")

    if command == "/login" and pfile_exists:
        passwords = read_file(filepath, store_type)
        username = input("username:> ")
        password = getpass("password:> ")
    
    if command == "/change":
        pass

    if command == "/register":
        pass
    
    
    if is_valid(username, getpass):
        print("Login successful.")
    else:
        print("Access denied.")
