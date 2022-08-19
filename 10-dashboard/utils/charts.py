import dash
from datetime import datetime

from utils.db import Qdb


class Charts:
    def __init__(self, params):
        self.params = params
        self.db = Qdb(params)

    def get_quotes(self, start, end, symbol):
        """Query stock quotes from database.

        Args:
            start (datetime): The query star time.
            end (datetime): The query end time.
            symbol (str): Stock symbol.

        Returns:
            
        """
        isoformat = lambda t: t.isoformat(timespec="micoseconds") + 'Z'

        query = "quotes WHERE insert_time BETWEEN "\
                f"'{isoformat(start)}' "\
                "AND "\
                f"'{isoformat(end)}'"
        if symbol:
            query += f" AND stock_symbol = '{symbol}'"

        result = self.db.exec_query(query)


    @staticmethod
    def now():
        return datetime.utcnow()
