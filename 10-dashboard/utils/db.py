import logging
import psycopg2 as pg

logger = logging.getLogger("qdb")

class Qdb:
    def __init__(self, params):
        self.params = params

    def create_table(self):
        logger.info("creating quotes tables in database if it doesn't already exists")
        connection = None
        cursor = None
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
            logger.error("error occured during creating quotes table in database: {err}", exc_info=True)
            raise SystemExit()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                logger.info("connection to database closed")

        return result

