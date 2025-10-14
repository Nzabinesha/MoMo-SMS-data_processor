#!/usr/bin/env python3
"""
api/server.py
Simple REST API for MoMo SMS transactions
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dsa.parse_xml import parse_file

# Load data
transactions = parse_file()
tx_dict = {tx["internal_id"]: tx for tx in transactions}

# Basic Auth setup
USERNAME = "admin"
PASSWORD = "1234"

def check_auth(header):
    if not header or not header.startswith("Basic "):
        return False
    encoded = header.split(" ")[1]
    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
        user, pwd = decoded.split(":", 1)
        return user == USERNAME and pwd == PASSWORD
    except Exception:
        return False


class MoMoHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MoMoAPI"')
        self.end_headers()
        self.wfile.write(b'{"error": "Unauthorized"}')

    def do_GET(self):
        # Authentication
        if not check_auth(self.headers.get("Authorization")):
            return self._unauthorized()

        if self.path == "/transactions":
            self._set_headers()
            self.wfile.write(json.dumps(list(tx_dict.values()), indent=2).encode())
        else:
            match = re.match(r"^/transactions/(\d+)$", self.path)
            if match:
                tid = int(match.group(1))
                tx = tx_dict.get(tid)
                if tx:
                    self._set_headers()
                    self.wfile.write(json.dumps(tx, indent=2).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(b'{"error": "Transaction not found"}')
            else:
                self._set_headers(404)
                self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_POST(self):
        if not check_auth(self.headers.get("Authorization")):
            return self._unauthorized()

        if self.path == "/transactions":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                new_tx = json.loads(post_data)
                new_id = max(tx_dict.keys()) + 1
                new_tx["internal_id"] = new_id
                tx_dict[new_id] = new_tx
                self._set_headers(201)
                self.wfile.write(json.dumps({"message": "Transaction added successfully", "id": new_id}).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_PUT(self):
        if not check_auth(self.headers.get("Authorization")):
            return self._unauthorized()

        match = re.match(r"^/transactions/(\d+)$", self.path)
        if match:
            tid = int(match.group(1))
            if tid in tx_dict:
                content_length = int(self.headers.get("Content-Length", 0))
                data = self.rfile.read(content_length)
                updates = json.loads(data)
                tx_dict[tid].update(updates)
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": f"Transaction {tid} updated successfully"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(b'{"error": "Transaction not found"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_DELETE(self):
        if not check_auth(self.headers.get("Authorization")):
            return self._unauthorized()

        match = re.match(r"^/transactions/(\d+)$", self.path)
        if match:
            tid = int(match.group(1))
            if tid in tx_dict:
                del tx_dict[tid]
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": f"Transaction {tid} deleted successfully"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(b'{"error": "Transaction not found"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Endpoint not found"}')


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), MoMoHandler)
    print("✅ Server running on http://localhost:8000")
    server.serve_forever()

