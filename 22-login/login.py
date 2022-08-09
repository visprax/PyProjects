#!/usr/bin/env python3

import os
import configparser
from getpass import getpass

def isvalid(username, password):
    return True


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("login.conf")

    store_type = config["default"]["store_type"]
    if store_type not in ["db", "json", "yaml"]:
        raise SystemExit(f"'store_type': {store_type} in config file not supported.")
    store_path = config["default"]["store_path"]
    if not os.path.exists(store_path):
        raise SystemExit(f"'store_path': {store_path} in config file doesn't exist.")
    store_name = config["default"]["store_name"] + '.' + store_type

    username = input("Enter your username:> ")
    password = getpass("Enter your password:> ")
    
    if isvalid(username, getpass):
        print("Login successful.")
    else:
        print("Access denied.")
