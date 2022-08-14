#!/usr/bin/env python3

"""A simple blockchain application."""

import flask
import logging

from utils.blockchain import Blockchain

logger = logging.getLogger("xcoin")

# this is our node server in our blockchain network
app = flask.Flask("xcoin")







