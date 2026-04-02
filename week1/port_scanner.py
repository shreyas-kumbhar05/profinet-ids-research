
import socket

def scan_ports(target, start_port, end_port):
    print(f"Scanning {target}...")
    open_ports = []

    for port in range(start_port, end_port + 1):
        s = socket.socket()
        s.settimeout(0.5)
        result = s.connect_ex((target, port))
        if result == 0:
            print(f"  [OPEN] Port {port}")
            open_ports.append(port)
        s.close()

    print(f"Scan complete. {len(open_ports)} open ports found.")
    return open_ports

scan_ports("127.0.0.1", 1, 1024)
