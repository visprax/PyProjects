from celery import Celery
from finnhub import Client

from config_parser import read_config


celery = Celery(broker=params["celery"]["broker"])
client = Client(api_key=params["finnhub"]["key"])

def setup_periodic_tasks(sender, **kwargs):
    """Periodic tasks setup for each symbol."""
    sender.add_periodic_task()
