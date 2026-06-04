from scapy.all import *
import csv
import time

packet_count = 0

with open("packets_sample.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "timestamp",
        "source_ip",
        "destination_ip",
        "protocol",
        "packet_length"
    ])

    def log_packet(packet):

        global packet_count

        src = None
        dst = None
        proto = None

        if IP in packet:

            src = packet[IP].src
            dst = packet[IP].dst
            proto = packet[IP].proto

        elif IPv6 in packet:

            src = packet[IPv6].src
            dst = packet[IPv6].dst
            proto = packet[IPv6].nh

        else:
            return

        writer.writerow([
            time.time(),
            src,
            dst,
            proto,
            len(packet)
        ])

        packet_count += 1

        print(
            f"Captured {packet_count}: "
            f"{src} -> {dst} "
            f"Proto={proto} "
            f"Len={len(packet)}"
        )

    sniff(
        iface="eth0",
        count=100,
        prn=log_packet
    )

print("Capture Complete")
