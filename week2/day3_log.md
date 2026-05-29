
# Day 3 — Week 2 — 29/05/2026

**Hours Logged:** 2.5  
**Focus:** Real-World Traffic Analysis Using Wireshark

---

# What I Studied

- Wireshark Part 3: Analyzing Network Traffic
- Practical packet analysis using malware traffic captures from:
  - https://malware-traffic-analysis.net/
- Investigation techniques for:
  - HTTP traffic
  - DNS traffic
  - FTP traffic
  - SMTP (Email) traffic
  - Malware command-and-control communication

---

# Understanding Traffic Filtering

## Basic + DNS Filtering

To isolate potentially suspicious traffic while removing common web browsing noise, I used the following filter:

```wireshark
(http.request or tls.handshake.type == 1 or (tcp.flags.syn == 1 and tcp.flags.ack == 0) or dns) and !(ssdp)
```

This filter highlights:

- HTTP requests
- TLS Client Hello messages
- Initial TCP connection attempts
- DNS lookups

while excluding SSDP traffic.

---

# Practical Exercise 1 — Detecting Suspicious DNS Activity

## Dataset Used

- Packet capture associated with Ava Maria RAT
- Source: malware-traffic-analysis.net

## Observation

At first glance, the traffic appeared normal.

After applying the Basic + DNS filter, I observed DNS requests communicating with a `ddns.net` domain.

Dynamic DNS services are commonly used by attackers because they allow command-and-control infrastructure to change IP addresses without changing the domain name.

## Lesson Learned

Raw packet captures often appear harmless until unnecessary traffic is removed.

Effective filtering is critical for identifying attacker infrastructure hidden within legitimate traffic.

---

# Practical Exercise 2 — FTP Traffic Analysis

## FTP Filters Used

Display FTP commands:

```wireshark
ftp.request.command
```

Display FTP commands and associated data transfers:

```wireshark
ftp.request.command or (ftp-data and tcp.seq == 1)
```

## Observation

Using **Follow TCP Stream** allowed me to reconstruct the entire FTP session.

I was able to view:

- FTP commands
- Server responses
- File transfer activity

in plaintext.

## Lesson Learned

FTP provides no encryption by default.

Anyone with visibility into network traffic can potentially observe:

- usernames
- passwords
- transferred files

This highlights why encrypted alternatives such as SFTP and FTPS are preferred.

---

# Practical Exercise 3 — Email Traffic Analysis

## SMTP Filters Used

Display SMTP commands:

```wireshark
smtp.req.command
```

Display email content fragments:

```wireshark
smtp.data.fragment
```

Combined filter:

```wireshark
smtp.req.command or smtp.data.fragment
```

## Observation

A single host was sending emails to multiple recipients within a short period of time.

This behavior resembled automated bulk email distribution and could indicate phishing activity.

## Lesson Learned

Communication patterns can reveal suspicious behavior even before analyzing email contents.

High-volume outbound email activity should be investigated further.

---

# Practical Exercise 4 — Malware Investigation

## Initial Discovery

While reviewing a malware packet capture, I identified suspicious traffic involving:

```text
192.180.191.64
```

Following the HTTP stream revealed a User-Agent string associated with **NetSupport Manager**.

## Observation

NetSupport Manager is a legitimate remote administration tool.

However, threat actors frequently abuse it as a Remote Access Trojan (RAT).

This demonstrates that legitimate software can be repurposed for malicious activity.

---

## Verification Using VirusTotal

I extracted the suspicious URL from the HTTP POST request and submitted it to VirusTotal.

VirusTotal identified the URL as malicious.

I also reviewed community comments to gain additional context regarding the threat.

## Lesson Learned

Threat intelligence platforms provide valuable context during packet investigations and help validate suspicious indicators.

---

## Identifying the Victim

To gather information about the affected user, I analyzed LDAP traffic using:

```wireshark
ldap.AttributeDescription == "givenName"
```

## Observation

LDAP traffic revealed information about the compromised user account.

## Lesson Learned

Directory service traffic can provide valuable context during incident response investigations by linking network activity to specific users.

---

# Reconstructing the Attack Timeline

After identifying the malicious traffic, I investigated network activity that occurred immediately beforehand.

## Findings

### Stage 1

User visited:

```text
classicgrand.com
```

### Stage 2

Browser connected to:

```text
modandcrackedapk.com
```

approximately four seconds later.

### Stage 3

VirusTotal identified the second site as malicious.

### Stage 4

Traffic analysis suggested that `classicgrand.com` had been compromised and redirected visitors to the malicious domain.

### Stage 5

The malicious download likely resulted in malware execution and subsequent command-and-control communication.

---

# Reconstructed Attack Timeline

1. User visits `classicgrand.com`
2. Website redirects user to `modandcrackedapk.com`
3. Malicious software is downloaded
4. Malware executes
5. NetSupport RAT communication begins
6. System becomes compromised

---

# Filter Shortcuts Added

## basic

Purpose:

- Display successful connections
- Display established sessions

## basic+

Purpose:

- Identify web traffic
- Identify initial connection attempts
- Reduce SSDP noise

## basic+dns

Purpose:

- Identify domains contacted by a host
- Highlight DNS activity associated with suspicious traffic
- Assist in malware investigations

## ftp

Purpose:

- Display FTP control traffic
- Display FTP file transfer activity

## smtp

Purpose:

- Display email-related traffic
- Inspect SMTP communication patterns

---

# What Surprised Me

- FTP traffic is transmitted in plaintext and can be inspected easily.
- DNS traffic often provides early indicators of malicious communication.
- Malware investigations rely heavily on traffic patterns, not just malware binaries.
- Legitimate administration software such as NetSupport Manager can be abused by attackers.
- Building a timeline from packet captures can reveal the complete infection chain.

---

# Connection to Project 1

Although Project 1 focuses on PROFINET rather than web traffic, today's exercises reinforced several important concepts:

- Effective filtering dramatically reduces analysis noise.
- Communication patterns are often more useful than packet contents.
- Building an attack timeline is critical for understanding malicious behavior.
- Anomaly detection depends on identifying deviations from a normal traffic baseline.

These concepts will later apply directly to:

- PROFINET traffic analysis
- Replay attack detection
- Spoofed frame detection
- Feature extraction for machine learning models
- Network anomaly detection methodologies

---

# Questions for Further Study

- How can DNS activity be incorporated as a feature in anomaly detection systems?
- How do industrial protocols such as PROFINET expose behavioral indicators similar to those seen in web traffic?
- Can Wireshark Lua dissectors improve analysis of industrial protocols?
- How are command-and-control communication patterns identified automatically in enterprise IDS systems?

---

# Goal for Next Session

- Install Scapy
- Study packet crafting fundamentals
- Learn packet layers:
  - Ether()
  - IP()
  - TCP()
  - Raw()
- Learn the difference between:
  - send()
  - sendp()
- Begin implementation of `packet_logger.py`
- Capture packets programmatically
- Export packet data to CSV
