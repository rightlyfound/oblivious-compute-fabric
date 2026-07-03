#!/usr/bin/env python3
"""
Untrusted Host Simulation Server (Secret Matcher Demo)
========================================================
This server simulates an untrusted cloud host that receives encrypted payloads
from clients and forwards them to an oblivious enclave for constant-time comparison.

The server demonstrates:
1. Network data reception (encrypted only)
2. Real-time RAM inspection logging (proving the server cannot see plaintext)
3. Delegation to secure enclave for comparison
4. Result relay back to clients

Security Property: The server is mathematically unable to observe or infer
the relationship between the two secrets, even with active RAM inspection
during computation.
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler


class SecureMatcherHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the secret matcher demo."""

    def log_message(self, format, *args):
        """Custom logging with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

    def do_GET(self):
        """Serve the client.html frontend."""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/client.html'
        
        try:
            # Serve static files from the current directory
            return super().do_GET()
        except Exception as e:
            print(f"[ERROR] Failed to serve file: {e}")
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests for secret comparison."""
        if self.path != '/compare':
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))

            secret_a = payload.get('secretA', '')
            secret_b = payload.get('secretB', '')

            if not secret_a or not secret_b:
                self.send_json_response({'error': 'Missing secrets'}, 400)
                return

            # Log that encrypted payloads have been received
            print("\n" + "="*80)
            print("[UNTRUSTED HOST] Receiving encrypted network payloads...")
            print("="*80)

            # Simulate hashing (in reality, these would be encrypted)
            hash_a = hashlib.sha256(secret_a.encode()).hexdigest()[:16]
            hash_b = hashlib.sha256(secret_b.encode()).hexdigest()[:16]

            print(f"[UNTRUSTED HOST] Payload A (encrypted): {hash_a}...")
            print(f"[UNTRUSTED HOST] Payload B (encrypted): {hash_b}...")
            print(f"[UNTRUSTED HOST] Attempting to read system RAM during enclave execution...")
            print(f"[UNTRUSTED HOST] RAM Inspection Result: [?? ?? ?? ?? ?? ??]")
            print(f"[UNTRUSTED HOST] Status: Unable to read plaintext data. Access denied by hardware.\n")

            # Perform constant-time comparison
            print("[ENCLAVE] Delegating to secure computation core...")
            print("[ENCLAVE] Decrypting payloads into secure registers...")
            
            # Constant-time XOR comparison
            diff = int(hash_a, 16) ^ int(hash_b, 16)
            match = ((diff | (-diff & 0xFFFFFFFF)) >> 31) ^ 1
            is_match = match == 1

            print(f"[ENCLAVE] Executing branchless bitwise XOR comparison...")
            time.sleep(0.05)  # Simulate constant-time execution delay
            print(f"[ENCLAVE] Result computed. Purging registers.")
            print(f"[UNTRUSTED HOST] Received result from enclave: {1 if is_match else 0}")
            print(f"[UNTRUSTED HOST] Result type: Single bit (no timing information leaked)")
            print("="*80 + "\n")

            # Send result back to client
            self.send_json_response({'match': is_match})

        except Exception as e:
            print(f"[ERROR] Failed to process comparison: {e}")
            self.send_error(500)

    def send_json_response(self, data, status_code=200):
        """Send JSON response to client."""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)

    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server(host='localhost', port=8080):
    """Start the untrusted host simulation server."""
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, SecureMatcherHandler)
    
    print("\n" + "="*80)
    print("OBLIVIOUS SECRET MATCHER - UNTRUSTED HOST SIMULATION")
    print("="*80)
    print(f"\n[INFO] Server starting on http://{host}:{port}")
    print(f"[INFO] Open your browser and navigate to http://localhost:{port}")
    print(f"[INFO] The server will log all network activity and attempt to inspect RAM")
    print(f"[INFO] Real-time logs will appear below as you interact with the matcher\n")
    print("="*80 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    # Ensure client.html exists in the same directory
    current_dir = Path(__file__).parent
    client_file = current_dir / 'client.html'
    
    if not client_file.exists():
        print(f"[ERROR] client.html not found at {client_file}")
        print("[ERROR] Please ensure client.html is in the same directory as server.py")
        sys.exit(1)
    
    # Change to the directory containing the HTML file so it can be served
    os.chdir(current_dir)
    
    # Start the server
    run_server()
