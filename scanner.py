#!/usr/bin/env python3
"""
Port Scanner - Network Reconnaissance Tool
Author: Vyshnav R
GitHub: github.com/Vyshnav7878
"""

import socket
import sys
import threading
from datetime import datetime

# Results storage
open_ports = []
lock = threading.Lock()

def scan_port(target, port):
    """Scan a single port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            with lock:
                open_ports.append((port, service))
                print(f"[+] Port {port:5d}/tcp  OPEN  {service}")
        sock.close()
    except:
        pass

def banner_grab(target, port):
    """Grab service banner"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((target, port))
        sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        return banner
    except:
        return None

def scan(target, start_port, end_port):
    """Main scanning function"""
    print(f"""
╔══════════════════════════════════════╗
║         PYTHON PORT SCANNER          ║
║         Author: Vyshnav R            ║
╚══════════════════════════════════════╝
    """)
    
    print(f"[*] Target   : {target}")
    print(f"[*] Ports    : {start_port} - {end_port}")
    print(f"[*] Started  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Scanning...\n")

    # Resolve hostname
    try:
        target_ip = socket.gethostbyname(target)
        print(f"[*] IP Address: {target_ip}\n")
    except:
        print(f"[-] Could not resolve {target}")
        sys.exit(1)

    # Thread pool for fast scanning
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(target_ip, port))
        threads.append(t)
        t.start()
        # Control thread count
        if len(threads) >= 100:
            for t in threads:
                t.join()
            threads = []

    # Wait for remaining threads
    for t in threads:
        t.join()

    # Summary
    print(f"\n[*] Scan Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Open ports found: {len(open_ports)}")
    
    if open_ports:
        print("\n[*] Attempting banner grabbing on open ports...")
        for port, service in sorted(open_ports):
            banner = banner_grab(target, port)
            if banner:
                print(f"[+] Port {port} banner: {banner[:100]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 scanner.py <target> <start_port> <end_port>")
        print(f"Example: python3 scanner.py localhost 1 1000")
        sys.exit(1)
    
    target = sys.argv[1]
    start_port = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_port = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    scan(target, start_port, end_port)
