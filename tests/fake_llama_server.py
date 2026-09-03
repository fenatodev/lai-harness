import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


class FakeLlamaServer:
    def __init__(
        self,
        api_key="synthetic-test-key",
        responder=None,
        require_auth=True,
    ):
        self.api_key = api_key
        self.require_auth = require_auth
        self.responder = responder or self.default_responder
        self.requests = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def send_json(self, status, payload):
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def authorized(self):
                return (
                    not owner.require_auth
                    or self.headers.get("Authorization") == f"Bearer {owner.api_key}"
                )

            def do_GET(self):
                owner.requests.append(("GET", self.path, dict(self.headers), None))
                if self.path != "/props":
                    self.send_json(404, {"error": "not found"})
                elif not self.authorized():
                    self.send_json(401, {"error": "unauthorized"})
                else:
                    self.send_json(200, {"model": "fake-local-model"})

            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    self.send_json(400, {"error": "invalid json"})
                    return
                owner.requests.append(("POST", self.path, dict(self.headers), payload))
                if self.path != "/v1/chat/completions":
                    self.send_json(404, {"error": "not found"})
                elif not self.authorized():
                    self.send_json(401, {"error": "unauthorized"})
                else:
                    self.send_json(200, owner.responder(payload, owner.requests))

            def log_message(self, format, *args):
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.host, self.port = self.httpd.server_address
        self.thread = Thread(target=self.httpd.serve_forever, daemon=True)

    @staticmethod
    def default_responder(payload, requests):
        return {
            "choices": [{"message": {"role": "assistant", "content": "fake response"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9},
        }

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
