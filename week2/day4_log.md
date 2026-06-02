# Day 4 — Week 2 — 02/06/2026

**Hours Logged:** 2  
**Focus:** Introduction to TCPdump and Traffic Analysis

---

# What I Studied

- Introduction to TCPdump
- Analyzing network traffic using TCPdump
- Packet capture using command-line tools
- Basic Berkeley Packet Filter (BPF) syntax
- Reading and saving PCAP files

---

# What TCPdump Is

- TCPdump is a command-line packet analyzer
- Uses the libpcap library for packet capture
- Can capture live traffic or analyze saved PCAP files
- Lightweight alternative to Wireshark
- Commonly used on servers and remote systems

---

# Commands Learned

## List Available Interfaces

```bash
tcpdump -D
```

Displays all available capture interfaces.

---

## Capture Traffic on an Interface

```bash
sudo tcpdump -i eth0
```

Captures packets from the selected interface.

---

## Capture Limited Number of Packets

```bash
sudo tcpdump -i eth0 -c 10
```

Stops after capturing 10 packets.

---

## Disable Hostname Resolution

```bash
sudo tcpdump -i eth0 -nn
```

Shows raw IP addresses and port numbers.

Benefits:
- Faster output
- Easier investigation
- No DNS lookup delays

---

## Save Traffic to a PCAP File

```bash
sudo tcpdump -i eth0 -w capture.pcap
```

Stores captured packets for later analysis.

---

## Read a PCAP File

```bash
tcpdump -r capture.pcap
```

Displays packets stored in a PCAP file.

---

# Filtering Traffic

## Capture TCP Traffic

```bash
tcpdump tcp
```

---

## Capture UDP Traffic

```bash
tcpdump udp
```

---

## Capture DNS Traffic

```bash
tcpdump port 53
```

---

## Capture HTTPS Traffic

```bash
tcpdump port 443
```

---

## Filter by Host

```bash
tcpdump host 192.168.1.10
```

Shows traffic involving the specified host.

---

## Filter by Source

```bash
tcpdump src host 192.168.1.10
```

Shows packets originating from the host.

---

## Filter by Destination

```bash
tcpdump dst host 192.168.1.10
```

Shows packets sent to the host.

---

# BPF Syntax

TCPdump uses Berkeley Packet Filter syntax.

Common operators:

```text
and
or
not
```

Example:

```bash
tcpdump host 192.168.1.10 and port 80
```

Captures HTTP traffic involving the specified host.

---

# Key Observations

- Packet captures become difficult to analyze without filters.
- The `-nn` option makes output significantly easier to read.
- TCPdump is useful for quickly identifying traffic patterns.
- Traffic can be captured using TCPdump and later analyzed in Wireshark.
- Most investigations begin with broad filters and gradually narrow down.

---

# What Surprised Me

- Meaningful packet analysis can be performed entirely from the terminal.
- TCPdump is much faster than Wireshark for quick investigations.
- A few well-chosen filters can reduce thousands of packets to a manageable dataset.
- TCPdump and Wireshark complement each other rather than replace each other.

---

# Connection to Project 1

- TCPdump provides an additional method for collecting packet captures.
- BPF filtering can reduce noise before feature extraction.
- Capturing only relevant traffic will improve dataset quality.
- Understanding packet capture workflows will help when collecting PROFINET traffic in later weeks.

---

# Questions for Further Study

- Can TCPdump filter traffic using EtherType values?
- How does TCPdump internally interact with libpcap?
- How do TCPdump filters compare with Scapy sniff filters?
- What are the limitations of TCPdump compared to Wireshark?

---

# Goal for Next Session

- Install Scapy
- Learn packet construction using:
  - Ether()
  - IP()
  - TCP()
  - Raw()
- Learn:
  - sniff()
  - send()
  - sendp()
- Begin implementation of packet_logger.py
