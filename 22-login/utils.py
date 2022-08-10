import os
import json
import yaml
import sqlite3
import logging
import hashlib

logger = logging.getLogger("utils")

def get_hash(string):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()

def register_user(username, password, store_type, passwords_path):
    if store_type == "yaml":
        logger.debug(f"opening passwords file: '{passwords_path}'")
        with open(passwords_path, 'r+') as yamlfile:
            data = yaml.safe_load(yamlfile)
            for entry in data:
                if entry["username"] == username:
                    logger.debug(f"username: {username} already registered")
                    print("Username exists.")
                    return False
            entry = {"username": username, "password_hash": get_hash(password)}
            data.append(entry)
            logger.debug("writing updated data to: '{passwords_path}'")
            yaml.safe_dump(data, yamlfile)
        return True

    elif store_type == "json":
        logger.debug(f"opening passwords file: '{passwords_path}'")
        with open(passwords_path, 'r+') as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                if entry["username"] == username:
                    logger.debug(f"username: {username} already registered")
                    print("Username exists.")
                    return False
            entry = {"username": username, "password_hash": get_hash(password)}
            data.append(entry)
            logger.debug("writing updated data to: '{passwords_path}'")
            json.dump(data, jsonfile)
        return True

    else:
        just_created_database = False
        if not os.path.isfile(passwords_path):
            logger.debug(f"passwords database: '{passwords_path}' doesn't exist, creating")
            conn = sqlite3.connect(passwords_path)
            curs = conn.cursor()
            query = "CREATE TABLE users (username VARCHAR, password_hash VARCHAR)"
            conn.commit()
            curs.close()
            conn.close()
            just_created_database = True

        logger.debug(f"connecting to passwords database: '{passwords_path}'")
        conn = sqlite3.connect(passwords_path)
        curs = conn.cursor()
        # check if username is in database if we didn't just created it
        if just_created_database:
            logger.debug(f"inserting user to the databse")
            query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            curs.execute(query, (username, get_hash(password)))
            conn.commit()
        else:
            logger.debug(f"checking availability of the username")
            query = "SELECT * FROM users WHERE username = ?"
            result = curs.execute(query, (username,)).fetchone()
            conn.commit()
            if result:
                logger.debug(f"username: {username} already registered")
                print("Username exists.")
                return False
            else:
                query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                curs.execute(query, (username, get_hash(password)))
                conn.commit()
        curs.close()
        conn.close()
        return True

def change_password(username, password, store_type, passwords_path):
    if store_type == "yaml":
        logger.debug(f"opening yaml passwords file: '{passwords_path}'")
        with open(passwords_path, "r+") as yamlfile:
            data = yaml.safe_load(yamlfile)
            for entry in data:
                if entry["username"] == username:
                    entry.update({"password_hash": get_hash(password)})
                    break
            yaml.safe_dump(data, yamlfile)

    elif store_type == "json":
        logger.debug(f"opening json passwords file: '{passwords_path}'")
        with open(passwords_path, "r+") as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                if entry["username"] == username:
                    entry.update({"password_hash": get_hash(password)})
            json.dump(data, jsonfile)

    else:
        logger.debug(f"connection to password database: '{passwords_path}'")
        conn = sqlite3.connect(passwords_path)
        curs = conn.cursor()
        query = "UPDATE users SET password_hash = ? WHERE username = ?"
        curs.execute(query, (username, get_hash(password)))
        logger.debug(f"executed query on database.")
        conn.commit()
        curs.close()
        conn.close()

def login_user(username, password, store_type, passwords_path):
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
        conn = sqlite3.connect(passwords_path)
        curs = conn.cursor()
        query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
        entry = curs.execute(query, (username, get_hash(password))).fetchone()
        logger.debug(f"executed query on database.")
        conn.commit()
        curs.close()
        conn.close()
        return entry is not None
