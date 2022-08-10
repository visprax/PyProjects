#!/usr/bin/env python3

import os
import logging
import argparse
from getpass import getpass

from utils.parselib import validate_config
from utils.loginlib import login_user, change_password, register_user

# TODO: get username and email from command line
# TODO: email notifications

def main():
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
        log_level = "ERROR"
    elif args.v == 2:
        log_level = "INFO"
    else:
        log_level = "DEBUG"

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(log_level)

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

    config = validate_config(config_filepath)
    
    if args.command == "login":
        username = input("username:> ")
        password = getpass("password:> ")

        logger.info(f"attempting to login with username: '{username}'")
        if login_user(username, password, config["store_type"], config["passwords_path"]):
            print("Login successful.")
        else:
            print("Access denied.")

    elif args.command == "change":
        username = input("username:> ")
        password = getpass("old password:> ")
        if login_user(username, password, config["store_type"], config["passwords_path"]):
            logger.info(f"attempting to change password for username: '{username}'")
            # 3 tries for changing password in case the two passwords don't match
            tries = 0
            while tries < 3:
                tries += 1
                password1 = getpass("new password:> ")
                password2 = getpass("confirm password:> ")
                if password1 == password2:
                    change_password(username, password1, config["store_type"], config["passwords_path"])
                    break
                else:
                    print("Passwords don't match.")
            if tries == 3:
                logger.error("maximum tries for changing password is reached")
                print("Try again later.")
                raise SystemExit()
        else:
            logger.error(f"username: '{username}' and password doesn't match an entry")
            print("Username or Password doesn't exist.")
            raise SystemExit()

    else:
        username = input("username:> ")
        tries = 0
        while tries < 3:
            tries += 1
            password1 = getpass("password:> ")
            password2 = getpass("confirm password:> ")
            if password1 == password2:
                result = register_user(username, password1, config["store_type"], config["passwords_path"])
                if result:
                    print("Username creation successful.")
                else:
                    print("Username creation failed.")
                break
            else:
                print("Passwords don't match.")
        if tries == 3:
            logger.error("maximum tries for setting password is reached")
            print("Try again later.")
            raise SystemExit()


if __name__ == "__main__":
    main()
