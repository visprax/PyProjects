
"""A simple TCP/IP server implementation."""

import os
import logging
import http.server

logger = logging.getLogger("tcp")

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """Handle HTTP requests."""

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

    error_page = """\
    <html>
    <body>
        <h3> Access Error! </h3>
        <p>Error while accessing: {path}</p>
        <p>{err}</p>
    </html>
    </body>
    """

    def do_GET(self):
        """Overwrite the base method to handle GET requests."""
        logger.debug("handling GET request")
        try:
            abs_path = os.getcwd() + self.path
            if not os.path.exists(abs_path):
                raise RuntimeError(f"'{abs_path}': not found")
            elif os.path.isfile(abs_path):
                self.handle_file(abs_path)
            else:
                raise NotImplementedError("'{abs_path}': unknown object")
        except Exception as err:
            self.handle_error(err)

    def handle_file(self, path):
        try:
            # TODO: avoid reading whole file into memory!
            with open(path, 'rb') as f:
                content = f.read()
            self.send_content(content)
        except IOError as err:
            self.handle_error(err)

    def handle_error(self, err):
        """Handle error page and error log."""
        logger.error(f"exception occured during handling GET request", exc_info=True)
        content = self.error_page.format(path=self.path, err=err).encode("utf-8")
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        """Handle response creation and sending."""
        logger.debug("creating response and sending it")
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _dynamic_response(self):
        """Respond with a static page, generated on the fly."""
        logger.debug("dynamically responding with an on-the-fly generated page")
        vals = {
                "date_time"   : self.date_time_string(),
                "client_host" : self.client_address[0],
                "client_port" : self.client_address[1],
                "command"     : self.command,
                "path"        : self.path
                }
        content = self.page.format(**vals).encode("utf-8")
        self.send_content(content, 200)
