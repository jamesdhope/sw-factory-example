import http.server
import socketserver
import os
import json

PORT = 8000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Redirect root to static/index.html
        if self.path == '/':
            self.path = '/static/index.html'
        return super().do_GET()

if __name__ == "__main__":
    # Ensure status.json exists
    if not os.path.exists("status.json"):
        with open("status.json", "w") as f:
            json.dump({"state": "IDLE", "message": "Waiting for factory...", "objective": "-", "project": "-", "build_dir": "-", "history": []}, f)

    print(f"--- Software Factory Dashboard starting at http://localhost:{PORT} ---")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
            httpd.server_close()
