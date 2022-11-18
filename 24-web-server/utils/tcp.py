
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
        <table>  
            <tr>  <td>Header</td>        <td>Value</td>          </tr>
            <tr>  <td>Date & Time:</td>  <td>{date_time}</td>    </tr>
            <tr>  <td>Client Host:</td>  <td>{client_host}</td>  </tr>
            <tr>  <td>Client Port:</td>  <td>{client_port}</td>  </tr>
            <tr>  <td>Command:</td>      <td>{command}</td>      </tr>
            <tr>  <td>Path:</td>         <td>{path}</td>         </tr>
        </table>
    </body>
    </html>
    """

    def do_GET(self):
        """Overwrites the base method to handle GET requests."""
        logger.debug("handling GET request")
        body = self.response_body()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def response_body(self):
        """Creates the response body to be sent by the server."""
        logger.debug("creating response body")
        vals = {
                "date_time"   : self.date_time_string(),
                "client_host" : self.client_address[0],
                "client_port" : self.client_address[1],
                "command"     : self.command,
                "path"        : self.path
                }
        resp = self.page.format(**vals).encode("utf-8")
        return resp

