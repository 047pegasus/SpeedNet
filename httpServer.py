import http.server
import socketserver

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

# Serve files from the current directory
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
