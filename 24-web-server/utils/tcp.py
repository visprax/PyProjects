
"""A simple TCP/IP server implementation."""

import logging
import http.server

logger = logging.getLogger("tcp")

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    page = """\
    <html>
    <body>
        <p> Hello Web Servers! </p><br>
    </body>
    </html>
    """

    def do_GET(self):
        """Overwrites base method to handle GET requests."""
        logger.debug("handling GET request")
        encoded_page = self.page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(encoded_page)))
        self.end_headers()
        self.wfile.write(encoded_page)
