#!/usr/bin/env python3
"""
Receives events from the MatrixPortal LED board.

On startup, registers this machine's callback URL with the board so it knows
where to send events — no manual IP configuration needed on either side.

Run with:
    python3 server.py
"""

import json
import socket
import urllib.request
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
BOARD_URL = "http://matrixportal.local"

def handle_event(event):
    if event == "person_detected":
        print("Person detected — do something here")
        # TODO: trigger Google Home routine, log it, send a notification, etc.

def register_with_board(my_url):
    payload = json.dumps({"url": my_url}).encode()
    req = urllib.request.Request(
        f"{BOARD_URL}/register",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            print(f"Registered with board: {result}")
    except Exception as e:
        print(f"Could not register with board: {e}")
        print("Board may not be up yet — events won't be received until it restarts or you re-run this script")

def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/events":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                event = data.get("event", "")
                print(f"Event: {event}")
                handle_event(event)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    ip = my_ip()
    my_url = f"http://{ip}:{PORT}/events"
    print(f"Starting on {my_url}")

    # register in background so the server is already listening when the board
    # tries to call back during testing
    httpd = HTTPServer(("", PORT), Handler)
    threading.Thread(target=lambda: register_with_board(my_url), daemon=True).start()

    httpd.serve_forever()
