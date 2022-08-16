#!/usr/bin/env python3

import logging
import requests

from utils.db import questdb_create_table

logger = logging.getLogger("stocks")

if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)

    response = questdb_create_table()
