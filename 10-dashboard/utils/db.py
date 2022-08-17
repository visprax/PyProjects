import logging
import psycopg2 as pg

logger = logging.getLogger("qdb")

class Qdb:
    def __init__(self, params):
        self.params = params
        logger.info("QuestDB instance created")

    def create_table(self):
        logger.info("creating quotes tables in database if it doesn't already exists")
        query = "CREATE TABLE IF NOT EXISTS "\
                    "quotes("\
                        "stock_symbol SYMBOL CAPACITY 5 CACHE INDEX, "\
                        "current_price DOUBLE, "\
                        "high_price DOUBLE, "\
                        "low_price DOUBLE, "\
                        "open_price DOUBLE, "\
                        "percent_change DOUBLE, "\
                        "trade_time TIMESTAMP, "\
                        "insert_time TIMESTAMP"\
                    ") "\
                    "timestamp(insert_time) "\
                "PARTITION BY DAY;"
        result = self.exec_query(query)
        return result

    def insert_quote(self, symbol, quote):
        logger.info(f"inserting {symbol} quotes into table")
        query = "INSERT INTO \
                    quotes("\
                        "stock_symbol, "\
                        "current_price, "\
                        "high_price, "\
                        "low_price, "\
                        "open_price, "\
                        "percent_change, "\
                        "trade_time, "\
                        "insert_time"\
                    ") "\
                    "VALUES("\
                        f"'{symbol}', "\
                        f"{quote['c']}, "\
                        f"{quote['h']}, "\
                        f"{quote['l']}, "\
                        f"{quote['o']}, "\
                        f"{quote['pc']}, "\
                        f"{quote['t']} * 1000000, "\
                        "systimestamp()"\
                    ");"
        result = self.exec_query(query)
        return result

    def exec_query(self, query):
        connection = None
        cursor = None
        try:
            connection = pg.connect(
                    user     = self.params["database"]["user"],
                    password = self.params["database"]["password"],
                    host     = self.params["database"]["host"],
                    port     = self.params["database"]["port"],
                    database = self.params["database"]["database"]
                    )
            cursor = connection.cursor()
            result = cursor.execute(query)
            connection.commit()
        except Exception as err:
            logger.error("error occured during query execution: {err}", exc_info=True)
            raise SystemExit()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                logger.info("connection to database closed")
        return result



