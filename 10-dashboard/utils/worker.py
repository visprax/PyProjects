import logging
from celery import Celery
from finnhub import Client

from utils.db import Qdb

logger = logging.getLogger("worker")

class Worker:
    def __init__(self, params):
        logger.info("setting up worker")
        self.params = params
        self.db = Qdb(params)

        logger.info("setting up Celery")
        self.celery = Celery("worker", broker=params["celery"]["broker"])
        logger.info("setting up Finnhub client")
        self.client = Client(api_key=params["finnhub"]["key"])

        @self.celery.on_after_configure.connect
        def setup_periodic_tasks(sender, **kwargs):
            """Periodic tasks setup for each symbol."""
            logger.info("setting up periodic tasks for each symbol")
            freq = self.params["finnhub"]["frequency"]
            for symbol in self.params["finnhub"]["symbols"]:
                sender.add_periodic_task(freq, fetch.s(symbol))

        @self.celery.task
        def fetch(symbol):
            """Fetch symbol quotes from Finnhub and insert into database."""
            # for an explanation on the quote structure, 
            # see: https://finnhub.io/docs/api/quote
            quote = self.client.quote(symbol)
            self.db.insert_quote(symbol, quote)
