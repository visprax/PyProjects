import os
import logging
import configparser

# TODO: jam finnhub section to the main loop also

logger = logging.getLogger("config")

def log_missing(section, key, default=None):
    """Log missing values from config file.

    Args:
        section (str): Which section in config file.
        key (str): Which key in the section.
        default (str): Default value for the missing key. Defaults to None.
    """
    if default:
        logger.warn(f"the setting for {key} in {section} in config file is missing, setting to default: {default}")
    else:
        logger.warn(f"the setting for {key} in {section} in config file is missing")

def strip_quotes(string):
    """Remove the single or double quotes. 

    This function removes the single or double quptes 
        put around strings when reading the config file 
        using the configparser module

    Args:
        string (str): The input string.

    Returns:
        str: The stipped string.
    """
    if string.startswith('"'):
        string = string.strip('"')
    elif string.startswith("'"):
        string = string.strip("'")
    else:
        pass
    return string

def read_config(filepath):
    """Read config file and perform validity check.

    Args:
        filepath (str): The path to config file.

    Returns:
        dict: The dictionary of parsed and value checked input settings.
    """
    logger.info(f"reading config file: {filepath}")
    config = configparser.ConfigParser()
    config.read(filepath)

    database_defaults = {
            "user": "admin",
            "password": "quest",
            "host": "127.0.0.1",
            "port": 8812,
            "database": "qdb",
            "pool_size": 4
            }
    celery_defaults = {"broker": "redis://127.0.0.1:6379/0"}
    plotly_defaults = {"interval": 10}
    finnhub_defaults = {
            "key": None,
            "frequency": 5,
            "symbols": ["AAPL", "AMZN", "EBAY"]
            }

    params = { 
        "database": database_defaults,
        "celery": celery_defaults,
        "plotly": plotly_defaults,
        }
    for section in params.keys():
        if section in config.sections():
            for key in params[section].keys():
                try:
                    if config[section][key]:
                        value = config[section][key]
                        value = strip_quotes(value)
                        params[section][key] = value
                except KeyError:
                    log_missing(section, key, params[section][key])
        else:
            logger.warn(f"{section} not in config file, setting to default values")

            
    
    try:
        finnhub_defaults["key"] = os.environ["FINKEY"]
    except KeyError:
        logger.warn("no FINKEY env is set, attempting to read from config file")
    if "finnhub" in config.sections():
        try:
            if not finnhub_defaults["key"] and config["finnhub"]["key"]:
                logger.warn("setting Finnhub API key from config file")
                key = config["finnhub"]["key"]
                key = strip_quotes(key)
                finnhub_defaults["key"] = key
        except KeyError:
            log_missing("finnhub", "key")

        try:
            if config["finnhub"]["frequency"]:
                frequency = config["finnhub"]["frequency"]
                frequency = strip_quotes(frequency)
                finnhub_defaults["frequency"] = frequency
        except KeyError:
            log_missing("finnhub", "frequency", finnhub_defaults["frequency"])

        try:
            if config["finnhub"]["symbols"]:
                symbols = config["finnhub"]["symbols"]
                symbols = strip_quotes(symbols)
                symbols = symbols.replace(' ', '').split(',')
                finnhub_defaults["symbols"] = symbols
        except KeyError:
            log_missing("finnhub", "symbols", finnhub_config["symbols"])
    else:
        logger.warn(f"{section} not in config file, setting to default values")

    if not finnhub_defaults["key"]:
        logger.critical("couldn't grab a value for Finnhub API key, can't continue")
        raise SystemExit()

    params["finnhub"] = finnhub_defaults
    return params





