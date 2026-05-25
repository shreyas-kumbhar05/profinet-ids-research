
# Day 2 — Week 2 — 25/05/2026
**Hours Logged:** 2  
**Focus:** Wireshark Profiles + Advanced Display Filtering

---

# What I Studied
- Wireshark Part 2: Configuring Profiles and Filters (Udemy)
- Practiced Wireshark display filter syntax manually
- Explored custom columns and protocol field references
- Learned how Wireshark profiles can optimize repeated packet analysis workflows

---

# Wireshark Profiles — What I Learned

- Wireshark profiles are customized analysis environments designed for specific packet analysis tasks
- Profiles store:
  - display filters
  - coloring rules
  - protocol preferences
  - custom columns
  - layout configurations
  - enabled/disabled dissectors

- Profiles allow fast switching between different network analysis contexts without repeatedly reconfiguring Wireshark manually
- Profiles are useful for:
  - web traffic analysis
  - malware traffic investigation
  - performance monitoring
  - incident response
  - industrial network traffic analysis

---

# Why Profiles Matter in Project 1

For Project 1, profiles will help separate different traffic analysis contexts.

## 1. Baseline Traffic Analysis

This profile can focus on:
- normal cyclic PROFINET communication
- timing consistency
- frame length patterns
- MAC address behavior

### Example Display Filter

```text
eth.type == 0x8892
```

This isolates PROFINET RT traffic from mixed Ethernet captures.

---

## 2. Attack Traffic Analysis

Separate profiles can help analyze:
- replay attacks
- spoofed frames
- malformed packets
- abnormal frame timing

### Example Filter

```text
eth.type == 0x8892 && frame.len > 60
```

This can help compare:
- normal vs anomalous frame sizes
- suspicious traffic bursts
- malformed traffic patterns

---

## 3. Timing Analysis

Profiles can configure timing-specific columns such as:
- frame.time_delta
- frame.time_relative
- frame.time_delta_displayed

This directly connects to Week 5 feature extraction where:
- inter-arrival time
- timing jitter
- cyclic timing consistency

become ML features for anomaly detection.

---

# Display Filters — What I Practiced

## HTTP Request Traffic

```text
http.request
```

Shows HTTP request packets.

---

## TLS Client Hello Packets

```text
tls.handshake.type == 1
```

Shows TLS Client Hello messages specifically.

Important clarification:
- This does NOT show all HTTPS traffic
- It only filters TLS handshake packets where the handshake type equals Client Hello

---

## Combined Filters

```text
http or tls
```

Shows packets matching either HTTP or TLS protocols.

---

## TCP SYN Packets

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Shows only initial TCP SYN packets.

This helps isolate TCP connection establishment attempts.

---

# Custom Columns — What I Learned

- Wireshark allows custom columns based on protocol fields
- Custom columns improve visibility during packet analysis

## Fields I Explored

### HTTP Hostname

```text
http.host
```

### TLS Server Name Indication (SNI)

```text
tls.handshake.extensions_server_name
```

This helps visualize application-layer destinations directly from packet captures.

---

# Practical Experiment

Created a custom profile named:

```text
Industrial Ethernet Analysis
```

Configured:
- Display filter:
  
```text
eth.type == 0x8892
```

Added custom columns:
- frame.time_delta_displayed
- eth.src
- eth.dst
- frame.len

Purpose:
- inspect cyclic communication timing
- analyze frame-size consistency
- prepare for PROFINET packet analysis in Week 3

---

# What Surprised Me

- Profiles are much more powerful than simple UI customization
- Different layouts significantly reduce cognitive load during packet analysis
- Timing-focused columns make cyclic communication visually easier to recognize
- Protocol-specific profiles can dramatically speed up anomaly investigation
- Wireshark field names are extremely granular and protocol-specific

---

# Connection to Project 1

- PROFINET RT traffic uses EtherType:

```text
0x8892
```

- Profiles will help permanently configure:
  - industrial traffic filters
  - timing-analysis layouts
  - packet-size inspection
  - MAC address visibility

- This will help later when:
  - validating generated traffic
  - inspecting replay attacks
  - comparing normal vs malicious captures
  - visually analyzing ML features before extracting them programmatically

- Timing columns in Wireshark directly relate to:
  - inter-arrival time features
  - cyclic timing analysis
  - anomaly detection logic

---

# Problems I Hit

- Initially confused capture filter syntax with display filter syntax again
- Had difficulty understanding Wireshark field naming conventions
- Needed documentation searches to understand:
  - nested protocol fields
  - filter operators
  - protocol-specific field references

- Realized that Wireshark filter syntax requires precise protocol field names and cannot be guessed reliably

---

# Questions I Still Have

- Can Wireshark decode custom protocols if I write a Lua dissector?
- How does Wireshark internally parse unknown EtherTypes?
- What is the exact difference between:
  - promiscuous mode
  - monitor mode
- How are timing columns calculated internally?
- How does Wireshark decide which dissector to apply to a packet?

---

# Key Concepts Reinforced Today

- Display filters operate AFTER packet capture
- Capture filters operate BEFORE packet capture
- Display filters use Wireshark syntax
- Capture filters use BPF syntax
- Profiles optimize repeated packet-analysis workflows
- Timing analysis is critical for industrial protocol anomaly detection

---

# What I Plan to Do Tomorrow

- Complete Wireshark Part 3: Analyzing Network Traffic (Udemy) 
- Complete Introduction to TCPdump section (Udemy) 
- Install Scapy: pip install scapy
- Read Scapy "Building packets" chapter at scapy.readthedocs.io
