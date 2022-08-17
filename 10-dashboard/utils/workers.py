import logging
from celery import Celery
from finnhub import Client

from utils.db import Qdb

logger = logging.getLogger("workers")

class Workers:
    def __init__(self, params):
        self.params = params
        self.celery = Celery(broker=params["celery"]["broker"])
        self.client = Client(api_key=params["finnhub"]["key"])
        self.db = Qdb(params)
        logger.info("workers are setup.")

    @self.celery.on_after_configure.connect
    def setup_periodic_tasks(self, sender):
        """Periodic tasks setup for each symbol."""
        logger.info("setting up periodic tasks for each symbol")
        freq = self.params["finnhub"]["frequency"]
        for symbol in self.params["finnhub"]["symbols"]:
            sender.add_periodic_task(freq, self.fetch.s(symbol))
    
    @self.celery.task
    def fetch(self, symbol):
        """Fetch symbol quotes from Finnhub and insert into database."""
        # for an explanation on the quote structure, 
        # see: https://finnhub.io/docs/api/quote
        quote = self.client.quote(symbol)
        self.db.insert_quote(symbol, quote)
