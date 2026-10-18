# PROFINET RT Frame — Byte-by-Byte Annotation

## Objective

This document provides a byte-level annotation of a manually constructed PROFINET RT frame generated during Week 3. The objective is to understand how raw Ethernet bytes map to protocol fields, how these fields are interpreted by protocol analyzers such as Wireshark, and how they can later be transformed into features for anomaly detection in an Industrial Intrusion Detection System (IDS).

---

# Source

Generated using:

`week3/profinet_frame.py`

Command:

```bash
sudo python3 week3/profinet_frame.py
```

The generated frame is intentionally minimal but structurally valid. It serves as the baseline frame for future traffic generation and feature extraction.

---

# Raw Hex Dump

```text
0000  01 0e cf 00 00 00 08 00 27 a0 f4 9c 88 92 80 01
0010  00 00 35 00 00 00 00 00 00 00 00 00 00 00 00 00
0020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0030  00 00 00 00 00 00 00 00 00 00 00 00
```

---

# Byte Annotation Table

## Ethernet Header (Bytes 0–13)

The Ethernet header identifies the sender, receiver and protocol carried by the frame. Unlike conventional enterprise traffic, PROFINET RT communicates directly over Ethernet without IP or TCP, making the Ethernet header critical for protocol identification.

| Bytes | Hex Values | Field | Specification | Explanation |
|-------|------------|-------|---------------|-------------|
| 0–5 | `01 0e cf 00 00 00` | Destination MAC | IEEE 802.3 | IEEE-registered PROFINET IO multicast address. It identifies the intended Ethernet receiver(s). An IDS expects this address to remain consistent within a baseline. Unexpected destination MAC addresses may indicate frame injection, network misconfiguration or unauthorized communication. |
| 6–11 | `08 00 27 a0 f4 9c` | Source MAC | IEEE 802.3 | MAC address of the transmitting device (Kali VM acting as a simulated IO Controller). This field establishes device identity. Changes may indicate MAC spoofing, unauthorized transmitters or device impersonation. |
| 12–13 | `88 92` | EtherType | IEEE 802.3 | EtherType 0x8892 identifies the payload as PROFINET RT. Wireshark and receiving devices use this value to invoke the PROFINET parser. Any unexpected EtherType indicates malformed traffic or an unexpected protocol. |

---

## PROFINET RT Header (Bytes 14–19)

The first six bytes following the Ethernet header contain protocol-specific information required for real-time industrial communication.

| Bytes | Hex Values | Field | Specification | Explanation |
|-------|------------|-------|---------------|-------------|
| 14–15 | `80 01` | FrameID | PROFINET IO RT | FrameID identifies the communication stream rather than an individual packet. The chosen value (0x8001) lies within the valid RT communication range (0x8000–0xBFFF). Unknown or unexpected FrameIDs may indicate abnormal protocol behaviour or configuration changes. |
| 16–17 | `00 00` | CycleCounter | PROFINET IO RT | Indicates communication cycle number. The first generated frame begins at CycleCounter = 0. During cyclic communication this value increments by exactly one every transmission cycle. Duplicate, missing or jumping values are valuable temporal indicators for anomaly detection. |
| 18 | `35` | DataStatus | PROFINET IO RT | Describes the validity and operational state of the transmitted process data. A value of 0x35 represents a healthy operating condition in this project. Unexpected changes may indicate device faults, invalid process data or abnormal operating conditions despite otherwise normal communication. |
| 19 | `00` | TransferStatus | PROFINET IO RT | Indicates the status of the communication transfer. A value of 0x00 represents a successful transfer. Non-zero values suggest communication-related problems even if the process data itself appears valid. |

---

## IO Data Payload (Bytes 20–59)

| Bytes | Hex Values | Field | Explanation |
|-------|------------|-------|-------------|
| 20–59 | `00 ... 00` | Cyclic IO Data | Forty bytes of zero-valued process data. Since no real PLC or IO Device is connected, these bytes act as placeholder cyclic process data while maintaining a valid frame length. |

---

# DataStatus (0x35) Bit-Level Analysis

```
0x35
↓

00110101
```

| Bit | Value | Meaning |
|------|-------|---------|
| 7 | 0 | Ignore bit cleared |
| 6 | 0 | DataValid indicates process data is valid |
| 5 | 1 | Reserved |
| 4 | 1 | Provider is operating normally |
| 3 | 0 | Reserved |
| 2 | 1 | No station problem indicated |
| 1 | 0 | Reserved |
| 0 | 1 | Primary Application Relationship (Primary AR) |

Although DataStatus occupies only one byte, it summarizes several aspects of device state. Unlike CycleCounter, which describes temporal behaviour, DataStatus reflects the health and validity of the industrial process.

---

# Why Each Value Was Chosen

| Field | Value | Reason |
|-------|-------|--------|
| Destination MAC | 01:0e:cf:00:00:00 | Standard PROFINET IO multicast address used by real implementations. |
| Source MAC | Kali VM MAC | Represents the simulated IO Controller generating traffic. |
| EtherType | 0x8892 | IEEE-assigned EtherType for PROFINET RT. |
| FrameID | 0x8001 | First easily recognizable valid RT FrameID used for debugging and future experimentation. |
| CycleCounter | 0 | Initial communication cycle. Will increment during traffic generation in Week 4. |
| DataStatus | 0x35 | Represents a healthy operational state for baseline traffic generation. |
| TransferStatus | 0x00 | Indicates successful communication transfer. |
| Payload | 40 bytes of zeros | Placeholder cyclic IO data in the absence of physical industrial devices. |

---

# Mapping Protocol Fields to Potential Attacks

| Attack Type | Field Affected | Normal Behaviour | Possible Anomalous Behaviour |
|-------------|---------------|------------------|------------------------------|
| Replay Attack | CycleCounter | Increments by exactly one | Duplicate or repeated counter values |
| MAC Spoofing | Source MAC | Fixed known MAC | Unknown or changing source MAC |
| Malformed Frame | FrameID | Valid RT range | Invalid or unexpected FrameID |
| Communication Failure | TransferStatus | 0x00 | Non-zero TransferStatus |
| Process Fault | DataStatus | Stable value (0x35) | Unexpected DataStatus transitions |
| Timing Attack | Inter-arrival Time | Stable cyclic timing | Increased latency or abnormal jitter |

---

# Connection to IDS Feature Extraction

Each protocol field can later become a measurable feature for anomaly detection.

| Protocol Field | Example Feature |
|---------------|-----------------|
| Source MAC | Known device verification |
| Destination MAC | Expected communication target |
| EtherType | Unexpected protocol detection |
| FrameID | FrameID frequency / validity |
| CycleCounter | Counter delta, duplicate detection, missing cycles |
| DataStatus | Process state monitoring |
| TransferStatus | Communication health monitoring |
| Inter-arrival Time | Timing anomaly detection |

---

# Key Research Insight

A PROFINET RT frame is more than a collection of bytes. Every field conveys a different aspect of industrial communication, including device identity, protocol identification, communication semantics, temporal consistency and process state. Understanding these fields at the byte level forms the foundation for protocol-aware feature engineering, enabling machine learning models to distinguish between normal industrial behaviour and anomalous activity.
