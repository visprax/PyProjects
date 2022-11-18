#!/usr/bin/env python3

import logging
import http.server

from utils.tcp import RequestHandler

logger = logging.getLogger("server")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.DEBUG)

    server_address = ('', 8090)
    try:
        server = http.server.HTTPServer(server_address, RequestHandler)
        server.serve_forever()
    except Exception as err:
        logger.error("an exception occured when starting the server", exc_info=True)

