# week1/pcap_reader.py
import dpkt
import socket

def read_pcap(file_path):
    print(f"Reading: {file_path}\n")
    
    with open(file_path, "rb") as f:
        pcap = dpkt.pcap.Reader(f)
        
        for timestamp, buf in pcap:
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                
                if not isinstance(eth.data, dpkt.ip.IP):
                    continue
                    
                ip = eth.data
                src_ip = socket.inet_ntoa(ip.src)
                dst_ip = socket.inet_ntoa(ip.dst)
                
                if ip.p == dpkt.ip.IP_PROTO_TCP:
                    protocol = "TCP"
                elif ip.p == dpkt.ip.IP_PROTO_UDP:
                    protocol = "UDP"
                elif ip.p == dpkt.ip.IP_PROTO_ICMP:
                    protocol = "ICMP"
                else:
                    protocol = f"OTHER({ip.p})"
                
                print(f"Time: {timestamp:.4f} | {src_ip} -> {dst_ip} | Protocol: {protocol}")
                
            except Exception as e:
                continue

read_pcap("sample.pcap")
