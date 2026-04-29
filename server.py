#!/usr/bin/env python3
"""
Receives events from the MatrixPortal LED board and acts on them.

Run with:
    python3 server.py

Board posts to http://<this machine>:8765/events with JSON:
    {"event": "person_detected"}
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

PORT = 8765

def handle_event(event):
    if event == "person_detected":
        print("Person detected — do something here")
        # TODO: trigger Google Home routine, log it, send a notification, etc.

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/events":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                event = data.get("event", "")
                print(f"Event received: {event}")
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
        pass  # silence default request logging

if __name__ == "__main__":
    print(f"Listening on port {PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()
