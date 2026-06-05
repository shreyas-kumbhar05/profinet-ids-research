from scapy.all import *

packet = IP(dst="8.8.8.8") / TCP(dport=443, flags="S")

print("=== SUMMARY ===")
print(packet.summary())

print("\n=== SHOW ===")
packet.show()

print("\n=== HEXDUMP ===")
hexdump(packet)
