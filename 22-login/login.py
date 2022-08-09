#!/usr/bin/env python3

import configparser
from getpass import getpass

def isvalid(username, password):
    return True


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("login.conf")

    username = input("Enter your username:> ")
    password = getpass("Enter your password:> ")
    
    if isvalid(username, getpass):
        print("Login successful.")
    else:
        print("Access denied.")
