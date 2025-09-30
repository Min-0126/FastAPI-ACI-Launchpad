# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hello from Dockerized Python!")

if __name__ == "__main__":
    server = HTTPServer(("", 8000), Handler)
    print("Serving on port 8000")
    server.serve_forever()
