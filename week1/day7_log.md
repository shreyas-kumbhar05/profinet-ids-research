**Date:** 11/04/2026<br>
**Week:** Week 1<br>
**Day:** Day 7  <br>
**Hours Logged:** 2<br>

---

##  Objective
- To build a pcap file using dpkt library 
- Parse layer 3 (IP layer) to print source IP, Destination IP, protocols
---

##  Concepts Learned

### What is PCAP
- **What:** PCAP is a binary log of network traffic which contains raw bytes of packets, metadata such as timestamps, length and also full protocol stack 
- **Why:** To store network traffic such as Ethernet, IP, TCP/UDP, Data
- **Tools using pcap:** Wireshark, tcpdump

### PCAP reader
- **What:** It opens a binary file, reads packets one by one, decodes the layers and extract useful information like source, destination IP, protocols

### dpkt
- **What:** It is a python module designed for packet creation and parsing, it supports around 63 protocols
- It has an object oriented design where packets are represented by a class, allowing users to parse raw data packets into human readable form.
---
## Implementation  
  
### PCAP Implementation  
- **What I built:**  
Built a PCAP reader in Python using the `dpkt` library to parse captured network packets and extract source IP, destination IP, and protocol information.  
  
- **How it works:**  
The script reads a `.pcap` file in binary mode and iterates through each packet. Each packet is decoded layer by layer:  
  
- Parses the **Ethernet layer** from raw packet bytes  
- Checks if the packet contains an **IP layer**  
- Extracts **source IP** and **destination IP**  
- Converts binary IP addresses into readable format using `socket.inet_ntoa()`  
- Identifies the **protocol (TCP / UDP / OTHER)** from the transport layer  
- Prints structured output for each packet
- **Command to run it:**
```bash
python3 pcap_reader.py 
```
- **Output I got:**
```
Time: 1775924698.5423 | 10.207.69.95 -> 172.217.26.46 | Protocol: TCP
Time: 1775924698.7472 | 172.217.26.46 -> 10.207.69.95 | Protocol: TCP
Time: 1775924698.7474 | 10.207.69.95 -> 172.217.26.46 | Protocol: TCP
Time: 1775924698.7475 | 10.207.69.95 -> 172.217.26.46 | Protocol: TCP
Time: 1775924699.2580 | 172.217.26.46 -> 10.207.69.95 | Protocol: TCP
Time: 1775924699.2582 | 172.217.26.46 -> 10.207.69.95 | Protocol: TCP
Time: 1775924699.2582 | 10.207.69.95 -> 172.217.26.46 | Protocol: TCP

```
- **Problems I hit:** Used wrong file mode (`"r"` instead of `"rb"`) for PCAP file
- **How I fixed them:** Opened file in binary mode using `"rb"`

---


##  Connections
### To the Project
-   Instead of actively scanning (like the port scanner), this enables **passive monitoring of real network traffic**.
-   It allows extraction of structured data (IP, protocol), which will later be:
    -   Stored in CSV format
    -   Used for detecting anomalies
    -   Fed into ML models for intrusion detection
### To Real World
Industrial systems (like PROFINET networks) rely on **packet inspection** to:

-   Detect unauthorized communication
-   Identify abnormal traffic patterns
-   Monitor protocol behavior in real time	


##  Next Steps
- Start  week 2 tomorrow
