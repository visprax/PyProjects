import os
import re
import logging
import configparser

logger = logging.getLogger("parser")

def validate_config(filepath):
    config = configparser.ConfigParser()
    logger.info(f"reading config file: '{filepath}'")
    config.read(filepath)
    
    try:
        store_type = config["default"]["store_type"]
        supported_store_types = ["db", "json", "yaml"]
        if store_type not in supported_store_types:
            message = f"'store_type': {store_type} in config file not supported"
            logger.critical(message)
            raise SystemExit(message)
    except KeyError:
        store_type = "db"

    try:
        store_path = config["default"]["store_path"]
        if not os.path.exists(store_path):
            message = f"'store_path': {store_path} in config file doesn't exist"
            logger.critical(message)
            raise SystemExit(message)
    except KeyError:
        store_path = "data"
    
    try :
        store_name = config["default"]["store_name"]
        store_name = store_name + '.' + store_type
    except KeyError:
        store_name = "passwords." + store_type 

    passwords_path = os.path.join(store_path, store_name)
    
    try:
        email_notif = config["default"]["email_notif"]
        if not email_notif in ["on", "off"]:
            message = f"'email_notif': {email_notif} in config file is not one of 'on' or 'off'"
            logger.critical(message)
            raise SystemExit(message)
    except KeyError:
        email_notif = "on"

    try:
        sender_email = config["default"]["sender_email"]
        # check sender email address has one @ sign with at least one . sign
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", sender_email):
            message = f"'sender_email': {sender_email} in config file seems not to be a valid email address"
            logger.critical(message)
            raise SystemExit(message)
    except KeyError:
        sender_email = "visprax@gmail.com"

    config = {
            "store_type": store_type,
            "store_path": store_path,
            "store_name": store_name,
            "passwords_path": passwords_path,
            "email_notif": email_notif,
            "sender_email": sender_email
            }
    return config
