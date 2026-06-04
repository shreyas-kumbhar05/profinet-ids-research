# Day 6 — Week 2 — 04/06/2026

**Hours Logged:** 2.5  
**Focus:** Building packet_logger.py and Generating Structured Packet Datasets

---

# What I Studied

- Packet sniffing using Scapy
- Packet logging and dataset generation
- Exporting network traffic to CSV format
- IPv4 and IPv6 packet handling
- Understanding packet flow from capture to dataset creation

---

# Packet Logger

## Objective

The main goal of the packet logger is to:

- Capture packets from a network interface
- Extract useful packet information
- Convert packet data into structured datasets
- Store results for future analysis and machine learning

Ultimately:

```text
Network Traffic
↓
Packet Capture
↓
Field Extraction
↓
CSV Dataset
↓
Feature Engineering
↓
Machine Learning
```

---

# Basic Scapy Concepts Used

## sniff()

Scapy function used to capture packets.

Example:

```python
sniff(count=10, prn=log_packet)
```

---

## count

Determines how many packets should be captured before stopping.

Example:

```python
count=10
```

Captures exactly 10 packets.

---

## prn

Specifies a callback function to execute whenever a packet is captured.

Example:

```python
prn=log_packet
```

For every captured packet:

```text
Packet Captured
↓
log_packet(packet)
↓
Process Packet
```

---

# Program 1 — Building the Basic Skeleton

## Code

```python
from scapy.all import sniff

def log_packet(packet):
    print(packet.summary())

sniff(count=10, prn=log_packet)
```

---

## Purpose

Understand how Scapy captures packets and passes them to a processing function.

---

## Visual Flow

```text
Network Traffic
↓
sniff()
↓
Packet Captured
↓
log_packet(packet)
↓
packet.summary()
↓
Display Output
```

---

## Output Analysis

### Packets 1–4

```text
Ether / IP / UDP 10.157.8.96:60986 > 239.255.255.250:1900 / Raw
```

Observation:

- Ether = Ethernet Frame (Layer 2)
- Source IP = 10.157.8.96
- Destination IP = 239.255.255.250
- Destination address is a multicast address
- Port 1900 is used by SSDP (Simple Service Discovery Protocol)

---

### Packet 5

```text
Ether / IP / UDP / BOOTP / DHCP Request
```

Observation:

- Device is requesting network configuration
- DHCP provides:
  - IP Address
  - Gateway
  - DNS Server

---

### Packet 6

```text
Ether / ARP who has 10.157.8.4 says 10.157.8.95
```

Observation:

Host:

```text
10.157.8.95
```

is asking:

```text
Who owns 10.157.8.4?
```

---

### Packet 7

```text
Ether / ARP is at 1a:5b:de:a4:d9:f1 says 10.157.8.4
```

Observation:

ARP reply:

```text
I am 10.157.8.4
My MAC address is 1a:5b:de:a4:d9:f1
```

---

### Packets 8–9

```text
Ether / IP / UDP / DNS Qry google.com
```

Observation:

System is performing DNS resolution.

Question:

```text
What IP address belongs to google.com?
```

---

### Packet 10

```text
Ether / IP / UDP / DNS Ans 142.250.77.78
```

Observation:

DNS server responds with:

```text
google.com = 142.250.77.78
```

---

# Program 2 — Building the Actual Packet Logger

## Code

```python
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
```

---

# Dataset Structure

Generated CSV fields:

| Field | Purpose |
|---------|---------|
| timestamp | Packet arrival time |
| source_ip | Sender address |
| destination_ip | Receiver address |
| protocol | Protocol identifier |
| packet_length | Packet size |

Example:

```csv
timestamp,source_ip,destination_ip,protocol,packet_length
1780593878.2471056,2409:...,2409:...,17,97
```

---

# Dataset Analysis

## Protocol Numbers Observed

### Protocol 6

```text
TCP
```

---

### Protocol 17

```text
UDP
```

---

### Protocol 58

```text
ICMPv6
```

---

# Key Observations

- Packet captures contain both IPv4 and IPv6 traffic.
- Modern systems frequently prefer IPv6 over IPv4.
- A single packet logger can handle multiple protocols using Scapy's packet parsing.
- Packet metadata can easily be converted into machine-learning datasets.

---

# Problems Encountered

## Problem 1 — No Packets Captured

Observation:

Program 1 worked correctly.

Program 2 captured nothing.

Cause:

Scapy was listening on the wrong network interface.

Solution:

Explicitly specified:

```python
iface="eth0"
```

Result:

Packet capture worked correctly.

---

## Problem 2 — Understanding Send vs Sniff

Important realization:

```text
send()
```

and

```text
sr1()
```

send packets using routing tables.

However:

```text
sniff()
```

listens only on a specific network interface.

If traffic exists on a different interface:

```text
Packets exist
↓
Traffic flows normally
↓
Scapy sees nothing
```

because it is listening in the wrong location.

---

## Problem 3 — IPv6 Preference

Observation:

Many packets appeared as:

```text
Ether / IPv6 / ICMPv6 Echo Request
```

Reason:

Operating system prefers IPv6 whenever available.

This explained why packet captures contained significantly more IPv6 traffic than expected.

---

## Problem 4 — Dataset Bias

Initially generated traffic using:

```bash
ping google.com -c 20
```

Result:

Dataset contained mostly:

- ICMPv6
- UDP
- IPv6

Very little TCP traffic.

Dataset became biased.

---

## Solution

Generated additional traffic:

```bash
curl https://google.com

curl https://github.com

curl https://stackoverflow.com

ping google.com -c 20
```

Result:

Dataset contained:

- DNS
- TCP
- TLS
- ICMPv6
- UDP

Much more balanced traffic distribution.

---

# What Surprised Me

- A simple packet logger can automatically generate structured datasets.
- Modern networks contain much more IPv6 traffic than expected.
- Capturing packets is easy; generating a useful dataset requires careful traffic generation.
- Choosing the wrong interface can completely hide existing traffic from Scapy.
- Packet captures can immediately be transformed into machine-learning datasets.

---

# Connection to Project 1

Today's work created the first complete version of the future IDS data pipeline.

Future workflow:

```text
Packet
↓
Field Extraction
↓
CSV Row
↓
Dataset
↓
Feature Engineering
↓
Machine Learning
↓
Intrusion Detection System
```

The packet logger is the first practical step toward building the anomaly detection system planned for Project 1.

---

# Goal for Next Session

- Commit remaining Week 2 work to GitHub
- Improve packet logger output formatting
- Explore additional packet features
- Begin thinking about feature extraction for anomaly detection
- Prepare for Week 3 industrial traffic analysis
