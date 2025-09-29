#!/usr/bin/env python3
# api/server.py
"""
Complete REST API using http.server
Provides CRUD on data/processed/transactions.json
Protects endpoints with Basic Auth (env vars: API_USER, API_PASS)
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from base64 import b64decode
from pathlib import Path
from typing import Tuple

# Config
DATA_FILE = Path("data/processed/transactions.json")
API_USER = os.environ.get("API_USER", "admin")
API_PASS = os.environ.get("API_PASS", "changeme")
PORT = int(os.environ.get("API_PORT", 8000))

# In-memory store
transactions = []

# Utilities for load/save
def load_data():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Auth helper
def check_basic_auth(header_value: str) -> bool:
    if not header_value or not header_value.startswith("Basic "):
        return False
    try:
        encoded = header_value.split(" ", 1)[1]
        decoded = b64decode(encoded).decode("utf-8")
        user, pwd = decoded.split(":", 1)
        return user == API_USER and pwd == API_PASS
    except Exception:
        return False

# HTTP Handler
class RequestHandler(BaseHTTPRequestHandler):
    def _auth_failed(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
        self.end_headers()
        self.wfile.write(b"Unauthorized")

    def _parse_id(self, path: str) -> Tuple[str, int]:
        parts = path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "transactions":
            try:
                return parts[0], int(parts[1])
            except ValueError:
                return parts[0], None
        return None, None

    # --- GET ---
    def do_GET(self):
        if not check_basic_auth(self.headers.get("Authorization")):
            return self._auth_failed()

        parsed = urlparse(self.path)
        # GET /transactions → list all
        if parsed.path == "/transactions":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(transactions).encode("utf-8"))
        else:
            # GET /transactions/{id} → single record
            kind, tid = self._parse_id(parsed.path)
            if kind == "transactions" and tid is not None:
                match = next((t for t in transactions if t.get("internal_id") == tid), None)
                if match:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(match).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")
            else:
                self.send_response(404)
                self.end_headers()

    # --- POST ---
    def do_POST(self):
        if not check_basic_auth(self.headers.get("Authorization")):
            return self._auth_failed()

        parsed = urlparse(self.path)
        if parsed.path != "/transactions":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            # Assign a new internal_id
            new_id = max((t["internal_id"] for t in transactions), default=0) + 1
            data["internal_id"] = new_id
            transactions.append(data)
            save_data(transactions)

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Bad Request: {e}".encode("utf-8"))

    # --- PUT ---
    def do_PUT(self):
        if not check_basic_auth(self.headers.get("Authorization")):
            return self._auth_failed()

        kind, tid = self._parse_id(urlparse(self.path).path)
        if kind != "transactions" or tid is None:
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            for i, t in enumerate(transactions):
                if t.get("internal_id") == tid:
                    transactions[i].update(data)
                    save_data(transactions)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(transactions[i]).encode("utf-8"))
                    return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Bad Request: {e}".encode("utf-8"))

    # --- DELETE ---
    def do_DELETE(self):
        if not check_basic_auth(self.headers.get("Authorization")):
            return self._auth_failed()

        kind, tid = self._parse_id(urlparse(self.path).path)
        if kind != "transactions" or tid is None:
            self.send_response(404)
            self.end_headers()
            return

        for i, t in enumerate(transactions):
            if t.get("internal_id") == tid:
                deleted = transactions.pop(i)
                save_data(transactions)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(deleted).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

# Run server
def run():
    global transactions
    transactions = load_data()
    print(f"✅ Loaded {len(transactions)} transactions from {DATA_FILE}")

    server_address = ("", PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"🚀 Server running on http://localhost:{PORT} (user={API_USER})")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

