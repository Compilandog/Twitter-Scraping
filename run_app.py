import webbrowser
import socket
from app import app


def find_port(start=5000, limit=5100):
    """Return first available port between start and limit."""
    port = start
    while port < limit:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No available ports")

if __name__ == "__main__":
    port = find_port()
    url = f"http://127.0.0.1:{port}"
    print(f"Starting server on {url}")
    webbrowser.open(url)
    app.run(host="0.0.0.0", port=port)
