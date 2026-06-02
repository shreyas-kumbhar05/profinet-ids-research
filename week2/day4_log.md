# Day 4 — Week 2 — 27/05/2026

**Hours Logged:** 2  
**Focus:** Introduction to TCPdump and Command-Line Traffic Analysis

---

# What I Studied

- Introduction to TCPdump
- Analyzing network traffic using TCPdump
- Basic packet capture techniques
- Traffic filtering using Berkeley Packet Filter (BPF) syntax
- Reading and analyzing packet captures from the command line

---

# What TCPdump Is

- TCPdump is a command-line packet analyzer used to capture and inspect network traffic. :contentReference[oaicite:0]{index=0}
- It uses the libpcap library to capture packets from network interfaces. :contentReference[oaicite:1]{index=1}
- Unlike Wireshark, TCPdump has no graphical interface and is designed for fast analysis from the terminal. :contentReference[oaicite:2]{index=2}
- TCPdump can capture live traffic or read previously saved PCAP files. :contentReference[oaicite:3]{index=3}

---

# Why TCPdump Matters

- Useful on remote servers where Wireshark cannot be installed.
- Lightweight and fast.
- Ideal for SSH sessions.
- Frequently used during incident response.
- Can capture traffic for later analysis in Wireshark. :contentReference[oaicite:4]{index=4}

---

# Basic Commands Learned

## List Interfaces

```bash
tcpdump -D
```

Shows available network interfaces. :contentReference[oaicite:5]{index=5}

---

## Capture on a Specific Interface

```bash
sudo tcpdump -i eth0
```

Captures packets on interface `eth0`.

---

## Limit Number of Packets

```bash
sudo tcpdump -i eth0 -c 10
```

Captures only 10 packets.

---

## Disable Name Resolution

```bash
sudo tcpdump -i eth0 -nn
```

Displays raw IP addresses and port numbers.

Reason:
- Faster output
- Avoids DNS lookups
- Better for investigations

---

# Understanding TCPdump Output

A packet entry typically contains:

- Timestamp
- Source IP
- Destination IP
- Protocol
- Port numbers
- Packet flags

Example:

```text
12:15:30 IP 192.168.1.10.443 > 192.168.1.20.55000
```

---

# Common Traffic Filters

## Capture Only TCP Traffic

```bash
tcpdump tcp
```

---

## Capture Only UDP Traffic

```bash
tcpdump udp
```

---

## Capture DNS Traffic

```bash
tcpdump port 53
```

---

## Capture HTTP Traffic

```bash
tcpdump port 80
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

Shows traffic involving a specific host.

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

# Reading Saved PCAP Files

## Open Existing Capture

```bash
tcpdump -r capture.pcap
```

Reads packets from a saved PCAP file. :contentReference[oaicite:6]{index=6}

---

## Save Captured Traffic

```bash
tcpdump -i eth0 -w capture.pcap
```

Writes captured traffic to a PCAP file. :contentReference[oaicite:7]{index=7}

---

# Key Concepts Learned

## Capture Filters

- Applied before packets are captured.
- Reduce storage usage.
- Improve capture performance.

Examples:

```bash
tcpdump port 80
```

```bash
tcpdump host 192.168.1.1
```

---

## BPF Syntax

TCPdump uses Berkeley Packet Filter (BPF) syntax.

Operators:

```text
and
or
not
```

Example:

```bash
tcpdump host 192.168.1.10 and port 80
```

---

# Practical Observations

- TCPdump is significantly faster than Wireshark for quick investigations.
- The `-nn` option makes output much easier to read.
- Most packet analysis tasks begin with filtering because raw traffic becomes overwhelming quickly.
- TCPdump and Wireshark work well together:
  - TCPdump captures traffic
  - Wireshark performs deep analysis

---

# What Surprised Me

- TCPdump can perform meaningful investigations without a GUI.
- Most packet captures become unreadable without filters.
- Many professional analysts begin investigations with TCPdump before opening Wireshark.
- The same PCAP file can be captured using TCPdump and analyzed later in Wireshark because both use libpcap-compatible formats. :contentReference[oaicite:8]{index=8}

---

# Connection to Project 1

- Week 2 requires packet capture and logging.
- TCPdump provides another method for collecting packet data before processing it with Python.
- Understanding BPF filtering will help reduce noise when capturing industrial traffic.
- Future PROFINET captures can be filtered before feature extraction.
- Capturing only relevant traffic reduces dataset size and preprocessing time.

---

# Questions for Further Study

- How does TCPdump capture packets internally using libpcap?
- How can TCPdump filters be translated into Scapy sniff filters?
- What are the performance differences between TCPdump and Wireshark on large captures?
- Can TCPdump capture PROFINET traffic using EtherType filters?

---

# Goal for Next Session

- Install Scapy
- Learn packet layer construction
- Understand:
  - Ether()
  - IP()
  - TCP()
  - Raw()
- Learn:
  - sniff()
  - send()
  - sendp()
- Begin implementation of packet_logger.py
- Capture packets and export them to CSV
