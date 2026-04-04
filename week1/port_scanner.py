import socket

def scan_ports(target, start_port, end_port):
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("Invalid hostname.")
        return

    print(f"Scanning {target} ({target_ip})...\n")
    open_ports = []

    try:
        for port in range(start_port, end_port + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)

            try:
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    print(f"[OPEN] Port {port}")
                    open_ports.append(port)
            except socket.error:
                pass
            finally:
                s.close()

    except KeyboardInterrupt:
        print("\nScan interrupted.")
        return

    print(f"\nScan complete. {len(open_ports)} open ports found.")
    return open_ports


scan_ports("127.0.0.1", 1, 10000)
