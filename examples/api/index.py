import json
import os
from http.server import BaseHTTPRequestHandler

import welcome_aboard.openhtf.main as openhtf
import welcome_aboard.vanilla.main as vanilla


class Handler(BaseHTTPRequestHandler):
    # Setting common CORS headers
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type")

    # Sending error response with appropriate CORS headers
    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

    # Handling preflight requests for CORS
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    # Handling POST requests
    def do_POST(self):
        auth_header = self.headers.get("Authorization")

        # Checking if Authorization header is present
        if not auth_header:
            self._send_error_response(401, "Missing Authorization header")
            return

        # Parsing the Authorization header
        try:
            _, api_key = auth_header.split(" ")
        except ValueError:
            self._send_error_response(
                400, "Invalid Authorization header format")
            return

        # Reading and parsing request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            body_data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            body_data = {}

        url = body_data.get("url", None)
        framework = body_data.get("framework", "openhtf")
        serial_number = body_data.get("serial_number", None)

        os.environ["TOFUPILOT_URL"] = url
        os.environ["TOFUPILOT_API_KEY"] = api_key

        # Calling the appropriate function based on the framework
        if framework == "vanilla":
            vanilla.main(serial_number)
        elif framework == "openhtf":
            openhtf.main(serial_number)

        # Sending success response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self._set_cors_headers()
        self.end_headers()

        response_body = {"message": "Request processed successfully"}
        self.wfile.write(json.dumps(response_body).encode("utf-8"))
