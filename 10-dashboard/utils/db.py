import logging
import requests

logger = logging.getLogger("db")

questdb_host = "http://localhost:9000"

def exec_query(query):
    logger.info("executing query on QuestDB")
    try:
        response = requests.get(questdb_host + "/exec?query=" + query)
        logger.debug(f"status code: {response.status_code}")
        response.raise_for_status()
    except Exception as err:
        logger.critical(f"error occured during executing query on QuestDB: {err}", exc_info=True)
        raise SystemExit()
    return response

def questdb_create_table():
    logger.info("checking the database tables")
    tables_query = "SHOW TABLES;"
    tables_resp = exec_query(tables_query)
    tables_dict = eval(tables_resp.text)
    try:
        dataset = tables_dict["dataset"]
        if "dataset" in tables_dict.keys() and ["quotes"] in tables_dict["dataset"]:
            logger.warn("quotes table already exists.")
            return tables_resp
        else:
            logger.info("creating quotes tables")
            create_query = "CREATE TABLE "\
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
            create_resp = exec_query(create_query)
            return create_resp
    except Exception as err:
        logger.error("error occured during creating quotes table in QuestDB: {err}", exc_info=True)
        raise SystemExit()
