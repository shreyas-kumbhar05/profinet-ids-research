
# Day 5 — Week 2 — 03/06/2026

**Hours Logged:** 2.5  
**Focus:** Scapy Fundamentals, TCP SYN Scanning, Packet Inspection

---

# What I Studied

- Scapy fundamentals
- Packet crafting
- TCP SYN scanning
- Packet inspection
- TCP flags
- Understanding packet structures before transmission

---

# Scapy Fundamentals

## Difference Between send() and sendp()

### send()

- Sends packets at Layer 3
- OS handles routing and Ethernet frame creation
- Used for IP-based packets

Example:

```python
send(IP(dst="8.8.8.8")/ICMP())
```

### sendp()

- Sends packets at Layer 2
- User controls Ethernet frame construction
- Used for custom Ethernet traffic

Example:

```python
sendp(Ether()/IP()/ICMP())
```

---

## Difference Between sr() and sr1()

### sr()

```python
ans, unans = sr(IP(dst="8.8.8.8")/ICMP())
```

- Send packet
- Receive multiple responses

### sr1()

```python
response = sr1(IP(dst="8.8.8.8")/ICMP())
```

- Send packet
- Return first response only

---

## Layer Stacking

```python
packet = IP(dst="8.8.8.8") / TCP(dport=443, flags="S")
```

Meaning:

```text
IP Layer
↓
TCP Layer
```

The TCP segment is placed inside the IP packet.

---

# Program 1 — Basic SYN Scan

## Code

```python
from scapy.all import IP, TCP, sr1

target = "127.0.0.1"
port = 80

packet = IP(dst=target) / TCP(dport=port, flags="S")

response = sr1(packet, timeout=2, verbose=0)

print(response)
```

## Output

```text
IP / TCP 127.0.0.1:http > 127.0.0.1:ftp_data RA
```

## Observation

- Received RST-ACK
- Port 80 is closed
- Connection request rejected

---

# Program 2 — Packet Field Inspection

## Code

```python
from scapy.all import IP, TCP, sr1

target = "127.0.0.1"
port = 80

packet = IP(dst=target) / TCP(dport=port, flags="S")

response = sr1(packet, timeout=2, verbose=0)

if response:
    response.show()
```

## Key Observations

### IP Header

```text
ihl = 5
len = 40
ttl = 64
```

- IP Header = 20 bytes
- TCP Header = 20 bytes
- Total Packet = 40 bytes

### TCP Header

```text
flags = RA
ack = 1
window = 0
```

- RST + ACK
- Connection rejected
- SYN consumed one sequence number

---

# TCP Flags

| Flag | Hex |
|--------|--------|
| FIN | 0x01 |
| SYN | 0x02 |
| RST | 0x04 |
| PSH | 0x08 |
| ACK | 0x10 |
| URG | 0x20 |

Examples:

```text
SYN + ACK = 0x12
RST + ACK = 0x14
```

---

# Program 3 — Port State Detection

## Code

```python
from scapy.all import *

target = "127.0.0.1"
port = 80

packet = IP(dst=target) / TCP(dport=port, flags="S")

response = sr1(packet, timeout=2, verbose=0)

if response and response.haslayer(TCP):

    tcp = response[TCP]

    if tcp.flags == 0x12:
        print("OPEN PORT")

    elif tcp.flags == 0x14:
        print("CLOSED PORT")

    else:
        print("OTHER RESPONSE")
```

## Observation

```text
0x12 → SYN-ACK → OPEN
0x14 → RST-ACK → CLOSED
```

This is the core logic used by SYN scanners.

---

# Program 4 — Packet Inspection

## Code

```python
from scapy.all import *

packet = IP(dst="8.8.8.8") / TCP(dport=443, flags="S")

print(packet.summary())

packet.show()

hexdump(packet)
```

---

## summary()

Output:

```text
IP / TCP 0.0.0.0:ftp_data > 8.8.8.8:https S
```

Purpose:

- Quick packet overview
- Shows protocol layers

---

## show()

Purpose:

- Displays all packet fields
- Useful for protocol analysis

Observation:

```text
ihl = None
len = None
chksum = None
```

Reason:

- Packet was created
- Packet was not transmitted
- Scapy has not finalized values yet

---

## hexdump()

Purpose:

- Displays raw bytes

Example:

```text
45 00 00 28 ...
```

Observation:

```text
45
```

Binary:

```text
0100 0101
```

Meaning:

```text
IPv4
IHL = 5
```

---

# Key Concepts Learned

- Packets in Scapy are Python objects.
- Packet fields become finalized during transmission.
- TCP flags are stored as bit values.
- Multiple flags can be active simultaneously.
- SYN packets consume one sequence number.
- Source IP and source port both identify a connection.

---

# What Surprised Me

- `response.show()` reveals every packet field.
- TCP flags are internally stored as hexadecimal values.
- A packet can exist as a Python object before it exists on the network.
- SYN scanning is essentially how Nmap's `-sS` scan works.

---

# Connection to Project 1

Today's work forms the foundation for future packet analysis.

Future IDS Pipeline:

```text
Raw Packet
↓
Field Extraction
↓
Feature Generation
↓
CSV Dataset
↓
Machine Learning Model
```

Understanding packet structure is required before building feature extraction and anomaly detection logic.

---

# Problems Encountered

- packet_logger.py not completed
- Need more practice reading packet fields
- Need to implement packet-to-CSV workflow

---

# Goal for Next Session

- Complete packet_logger.py
- Capture 100 packets
- Export packet data to CSV
- Analyze generated dataset
