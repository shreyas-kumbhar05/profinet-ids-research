from scapy.all import *

target = "127.0.0.1"
port = 8000

packet = IP(dst=target) / TCP(dport=port, flags="S")

response = sr1(packet, timeout=2, verbose=0)

if response:
    response.show()
    if response.haslayer(TCP):

        tcp = response[TCP]
        print(f"Target: {target}:{port}")
        print(f"Flags: {tcp.flags}")
	
        if tcp.flags == 0x12:
            print("OPEN PORT (SYN-ACK)")

        elif tcp.flags == 0x14:
            print("CLOSED PORT (RST-ACK)")

        else:
            print("OTHER RESPONSE:", tcp.flags)

else:
    print("NO RESPONSE (FILTERED)")
