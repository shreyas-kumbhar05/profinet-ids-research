# Feature Definitions — PROFINET IDS

This document defines the features extracted from PROFINET RT traffic,
why they are useful, and how they will be calculated by `extractor.py`.

## 1. Inter-Arrival Time (IAT)

- **What:** Time in seconds between consecutive captured frames
- **Calculation:** `np.diff(timestamps)`
- **Expected baseline:** approximately 0.004 seconds per cycle
- **Why:** PROFINET RT cyclic traffic is time-sensitive. Changes in
  inter-arrival time can indicate timing anomalies, delayed traffic or
  abnormal traffic bursts.
- **Detects:** Timing-based anomalies, flooding and delayed frames

## 2. Frame Size

- **What:** Total length of each captured Ethernet frame in bytes
- **Calculation:** `len(packet)`
- **Expected baseline:** 60 bytes for the current generator
- **Why:** The current simulated PROFINET connection uses a fixed payload
  size, so unexpected frame lengths can indicate malformed or modified
  traffic.
- **Detects:** Malformed frames and unexpected payload-length changes

## 3. EtherType Distribution

- **What:** Count or ratio of Ethernet EtherType values observed in a
  capture window
- **Calculation:** Group frames by `eth.type` and count occurrences
- **Expected baseline:** `0x8892` should dominate the normal PROFINET
  capture
- **Why:** EtherType identifies the protocol carried by the Ethernet
  frame. Unexpected protocol types can indicate traffic that does not
  belong to the expected communication.
- **Detects:** Protocol injection and unexpected traffic types

## 4. Source/Destination MAC Consistency

- **What:** Whether the source and destination MAC addresses belong to
  the established set for the session
- **Calculation:** Compare observed MAC addresses against the known
  baseline MAC set
- **Expected baseline:** Known controller/device MAC addresses only
- **Why:** PROFINET communication normally occurs between known network
  participants. A new or unexpected MAC address can indicate spoofing
  or another unauthorized participant.
- **Detects:** MAC spoofing and unexpected devices

## 5. Payload Entropy

- **What:** Shannon entropy of the PROFINET IO payload bytes
- **Calculation:** Count byte frequencies and calculate
  `-sum(p * log2(p) for p in probabilities)`
- **Expected baseline:** approximately 0 bits/byte for the current
  all-zero simulated payload
- **Why:** The baseline payload is constant, while significantly more
  diverse payload data can produce a higher entropy value.
- **Detects:** Payload modification, injection or corruption that changes
  the byte distribution

## Feature Summary

| Feature | Column Name | Type | Normal Baseline | Possible Anomaly Signal |
|---|---|---|---|---|
| Inter-arrival time | `iat` | float (seconds) | ~0.004 s target | Large timing deviation |
| Frame size | `frame_size` | integer (bytes) | 60 | Unexpected length |
| EtherType | `ethertype` | integer | 0x8892 | Unexpected protocol |
| MAC consistency | `mac_consistent` | boolean | True | False |
| Payload entropy | `payload_entropy` | float (bits/byte) | ~0.0 | Increase from baseline |

## Session Metadata

The extracted dataset should retain basic information about the capture
session:

- `session_id` — unique identifier for the capture run
- `capture_timestamp` — time when the capture was processed
- `cycle_time_ms` — configured generator cycle time
- `total_frames` — number of processed frames

Detailed implementation decisions are recorded in the Week 5 research
notes.
