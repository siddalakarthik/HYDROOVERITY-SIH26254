"""Loopback development API and bounded HTTPS proxy. No public deployment mode."""

import argparse
import http.client
import json
import logging
import os
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

from .config import Settings


class Proxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "HYDROOVERITY-local"

    def log_message(self, *args):
        pass

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def send_error(self, code, message=None, explain=None):
        payload = json.dumps(
            {
                "error": {
                    "code": "PROXY_REJECTED",
                    "message": "Local proxy request unavailable",
                    "request_id": str(uuid4()),
                    "field_errors": [],
                }
            }
        ).encode()
        self.send_response(code)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_request(self):
        if not self.path.startswith("/api/v1/"):
            self.send_error(404)
            return
        if self.headers.get("Transfer-Encoding"):
            self.send_error(400)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if not 0 <= length <= 16384:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        connection = http.client.HTTPConnection("127.0.0.1", 8000, timeout=10)
        try:
            allowed = {
                "content-type",
                "cookie",
                "origin",
                "referer",
                "sec-fetch-site",
                "x-csrf-token",
                "idempotency-key",
                "if-match",
                "accept",
                "last-event-id",
            }
            headers = {key: value for key, value in self.headers.items() if key.lower() in allowed}
            headers["Host"] = "127.0.0.1:8000"
            headers["X-Forwarded-For"] = self.client_address[0]
            headers["X-Forwarded-Proto"] = "https"
            connection.request(self.command, self.path, body=body, headers=headers)
            result = connection.getresponse()
            if self.command == "GET" and result.getheader("Content-Type", "").startswith(
                "text/event-stream"
            ):
                if connection.sock is not None:
                    connection.sock.settimeout(35)
                self.send_response(result.status)
                for key, value in result.getheaders():
                    if key.lower() not in {
                        "connection",
                        "transfer-encoding",
                        "content-length",
                        "server",
                        "date",
                    }:
                        self.send_header(key, value)
                self.send_header("Connection", "close")
                self.close_connection = True
                self.end_headers()
                self.connection.settimeout(5)
                try:
                    while payload := result.read1(8192):
                        self.wfile.write(payload)
                        self.wfile.flush()
                except (OSError, http.client.HTTPException):
                    pass  # Interrupted records require cursor replay or reset.
                return
            payload = result.read(1048577)
            if len(payload) > 1048576:
                self.send_error(502)
                return
            self.send_response(result.status)
            for key, value in result.getheaders():
                if key.lower() not in {
                    "connection",
                    "transfer-encoding",
                    "content-length",
                    "server",
                    "date",
                }:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (OSError, http.client.HTTPException):
            self.send_error(503)
        finally:
            connection.close()

    do_GET = do_POST = do_PATCH = do_PUT = do_DELETE = handle_request


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    api = sub.add_parser("api")
    api.add_argument("--runtime-config", type=Path, required=True)
    api.add_argument("--container-private", action="store_true")
    api.add_argument("--trusted-proxy-ip", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8000, choices=range(1024, 65536))
    proxy = sub.add_parser("proxy")
    proxy.add_argument("--certificate", type=Path, required=True)
    proxy.add_argument("--key", type=Path, required=True)
    args = p.parse_args()
    if args.command == "api":
        import uvicorn

        from .main import create_app

        settings = Settings.model_validate(json.loads(args.runtime_config.read_text()))
        # The child/API process receives runtime configuration only.
        for name in list(os.environ):
            if name in {"PGPASSWORD", "PGPASSFILE"} or name.startswith(
                (
                    "HYDRO_MIGRATION",
                    "HYDRO_OPERATOR",
                    "HYDRO_TEST_OWNER",
                    "HYDRO_TEST_ADMIN",
                    "HYDRO_BOOTSTRAP",
                )
            ):
                del os.environ[name]
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        uvicorn.run(
            create_app(settings),
            host="0.0.0.0" if args.container_private else "127.0.0.1",
            port=args.port,
            access_log=False,
            log_level="warning",
            proxy_headers=True,
            forwarded_allow_ips=args.trusted_proxy_ip,
        )
    else:
        server = ThreadingHTTPServer(("127.0.0.1", 8443), Proxy)
        server.timeout = 5
        server.socket.settimeout(10)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(str(args.certificate), str(args.key))
        server.socket = context.wrap_socket(server.socket, server_side=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
