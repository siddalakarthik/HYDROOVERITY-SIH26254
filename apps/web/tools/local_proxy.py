"""Optional private HTTPS frontend proxy; leaves the M03-only proxy unchanged."""

import argparse
import http.client
import json
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]


class Proxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "HYDROOVERITY-local-web"

    def log_message(self, *args):
        pass  # URLs, credentials and private request bodies never enter access logs.

    def reject(self, status):
        payload = json.dumps({"error": {"code": "PROXY_UNAVAILABLE", "message": "Local request unavailable", "request_id": "local-proxy", "field_errors": []}}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def request(self):
        parsed = urlsplit(self.path)
        decoded = unquote(parsed.path)
        if parsed.scheme or parsed.netloc or not decoded.startswith("/") or decoded.startswith("//") or "\\" in decoded or any(part in {"..", ".git", ".env", "internal"} for part in decoded.split("/")):
            self.reject(404)
            return
        is_api = decoded.startswith("/api/v1/")
        if not is_api and self.command not in {"GET", "HEAD"}:
            self.reject(405)
            return
        if self.headers.get("Transfer-Encoding"):
            self.reject(400)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.reject(400)
            return
        if not 0 <= length <= 16384:
            self.reject(413)
            return
        body = self.rfile.read(length)
        upstream = http.client.HTTPConnection("127.0.0.1", self.server.api_port if is_api else self.server.web_port, timeout=90)
        allowed = {"content-type", "cookie", "origin", "sec-fetch-site", "x-csrf-token", "idempotency-key", "if-match", "accept", "last-event-id", "rsc", "next-router-state-tree", "next-router-prefetch", "next-url"}
        headers = {key: val for key, val in self.headers.items() if key.lower() in allowed}
        headers.update({"Host": f"localhost:{self.server.server_port}", "X-Forwarded-Proto": "https", "X-Forwarded-For": self.client_address[0]})
        try:
            upstream.request(self.command, self.path, body=body, headers=headers)
            response = upstream.getresponse()
            if is_api and self.command == "GET" and response.getheader("Content-Type", "").startswith("text/event-stream"):
                self.send_response(response.status)
                for key, val in response.getheaders():
                    if key.lower() not in {"connection", "transfer-encoding", "content-length", "server", "date", "cache-control"}:
                        self.send_header(key, val)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.close_connection = True
                self.end_headers()
                self.connection.settimeout(5)
                try:
                    # read1 forwards available frames; read() buffers until EOF.
                    while payload := response.read1(8192):
                        self.wfile.write(payload)
                        self.wfile.flush()
                except (OSError, http.client.HTTPException):
                    pass  # A partial stream closes; replay/reset handles uncertainty.
                return
            payload = response.read(33554433)
            if len(payload) > 33554432:
                self.reject(502)
                return
            self.send_response(response.status)
            for key, val in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length", "server", "date", "cache-control"}:
                    self.send_header(key, val)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)
        except (OSError, http.client.HTTPException):
            self.reject(503)
        finally:
            upstream.close()

    do_GET = do_HEAD = do_POST = do_PATCH = do_PUT = do_DELETE = request


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--certificate", required=True, type=Path)
    p.add_argument("--key", required=True, type=Path)
    p.add_argument("--port", type=int, default=8443, choices=range(1024, 65536))
    p.add_argument("--api-port", type=int, default=8000, choices=range(1024, 65536))
    p.add_argument("--web-port", type=int, default=3000, choices=range(1024, 65536))
    args = p.parse_args()
    if any(path.resolve().is_relative_to(ROOT) for path in [args.certificate, args.key]):
        raise SystemExit("Keep certificates and private keys outside the checkout")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Proxy)
    server.api_port, server.web_port = args.api_port, args.web_port
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(args.certificate, args.key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print("Private frontend HTTPS proxy on https://localhost:8443", flush=True)
    server.serve_forever()
