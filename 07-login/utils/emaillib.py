import os
import ssl
import json
import yaml
import time
import sqlite3
import smtplib
import logging

# TODO: more accurate timestamp method (in terms of login time)
# TODO: check against null values for email column in sqlite database in get_receiver

logger = logging.getLogger("email")

def get_receiver(username, store_type, passwords_path):
    logger.info("getting username email address")
    if store_type in ["yaml", "json"]:
        if store_type == "yaml":
            logger.info(f"opening passwords json file: '{passwords_path}'")
            # we have done all the annoying checks in passlib module
            with open(passwords_path, 'r') as yamlfile:
                data = yaml.safe_load(yamlfile)
        else:
            logger.info(f"opening passwords yaml file: '{passwords_path}'")
            with open(passwords_path, 'r') as jsonfile:
                data = json.load(jsonfile)
        generator = (item for item in data if data["username"]==username)
        entry = next(generator)
        try:
            receiver = entry["email"]
        except KeyError:
            receiver = None
    else:
        logger.info("connecting to passwords database: '{passwords_path}'")
        conn = sqlite3.connect(passwords_path)
        curs = conn.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        entry = curs.execute(query, (username,)).fetchone()
        receiver = entry[-1]
    return receiver

def get_message(username, template):
    logger.info("constructing email message")
    now = time.strftime("%Y-%b-%d %H:%M:%S")

    if template == "login":
        message = """\
                Subject: XLOGIN successful login


                There was a successful login to you xlogin account (username: {}) at: {}""".format(username, now)
    elif template == "change":
        message = """\
                Subject: XLOGIN successful password change


                Your xlogin account (username: {}) password was changed successfully at: {}""".format(username, now)
    else:
        message = """\
                Subject: XLOGIN successful registration


                Your xlogin account (username: {}) was created successfully at: {}""".format(username, now)
    return message

def send_email(username, store_type, passwords_path, template):
    sender = "visprax@gmail.com"
    logger.info("reading environment variable: 'APP_PASS'")
    # this is the app password from google:
    # https://support.google.com/accounts/answer/185833?hl=en
    try:
        app_password = os.environ["APP_PASS"]
    except KeyError:
        message = "can't read ENV 'APP_PASS'"
        logger.error(message)
        raise SystemExit(message)

    receiver = get_receiver(username, store_type, passwords_path)
    if not receiver:
        logger.debug(f"no email record for username: '{username}'")
        return False

    message = get_message(username, template)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        logger.debug("loging to gmail server")
        server.login(sender, app_password)
        logger.debug("sending email message")
        server.sendmail(sender, receiver, message)
    return True

