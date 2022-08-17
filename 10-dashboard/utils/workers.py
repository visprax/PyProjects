import logging
from celery import Celery
from finnhub import Client

logger = logging.getLogger("workers")

class Workers:
    def __init__(self, params):
        self.params = params
        self.celery = Celery(broker=params["celery"]["broker"])
        self.client = Client(api_key=params["finnhub"]["key"])

    def setup_periodic_tasks(self):
        """Periodic tasks setup for each symbol."""
        pass

