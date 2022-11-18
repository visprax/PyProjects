
"""A simple TCP/IP server implementation."""

import logging
import http.server

logger = logging.getLogger("tcp")

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    def do_GET(self):
        """Overwrites base method to handle GET requests."""
        logger.debug("handling GET request")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page.encode("utf-8"))))
        self.end_headers()

        page = f"""\
        <html>
        <body>
            <p> Hello Web Servers! </p><br>
            <p> URL: {self.path} </p>
        </body>
        </html>
        """
        self.wfile.write(self.page)
