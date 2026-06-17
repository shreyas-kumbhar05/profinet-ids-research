# PROFINET RT Frame Structure

## Frame Layout Overview

A PROFINET RT frame is a standard Ethernet frame with EtherType 0x8892.
It contains no IP or TCP layer. The Ethernet payload carries the
PROFINET RT header directly, followed by cyclic process data.

```
Byte Offset    Length    Field
─────────────────────────────────────────
0              6         Destination MAC
6              6         Source MAC
12             2         EtherType (0x8892)
14             2         FrameID
16             2         CycleCounter
18             1         DataStatus
19             1         TransferStatus
20+            variable  Process Data (cyclic IO payload)
```

---

## Field-by-Field Reference

### Ethernet Header (Bytes 0–13)

| Bytes | Field | Length | Notes |
|---|---|---|---|
| 0–5 | Destination MAC | 6 bytes | IO multicast: `01:0e:cf:00:00:00` |
| 6–11 | Source MAC | 6 bytes | IO Controller MAC address |
| 12–13 | EtherType | 2 bytes | `0x8892` — PROFINET RT identifier |

**Destination MAC `01:0e:cf:00:00:00`:** This is the registered PROFINET
IO multicast MAC address. All IO Controllers in a PROFINET system send
cyclic data to this address. Seeing this destination MAC in a capture
is the first confirmation that the frame is PROFINET RT traffic.

---

### PROFINET RT Header (Bytes 14–19)

#### FrameID (Bytes 14–15, 2 bytes, big-endian)

- Identifies the type and purpose of this communication stream
- Stays constant throughout one IO connection session
- Valid range for RT Class 1/2/3: `0x8000–0xBFFF`

**IDS relevance:**
- FrameID outside valid range → malformed frame
- New FrameID appearing mid-session → unexpected device or protocol abuse
- FrameID changing between frames in the same session → spoofed frame

---

#### CycleCounter (Bytes 16–17, 2 bytes, big-endian)

- Increments by 1 with every transmitted cycle
- Range: 0–65535, wraps around to 0 after 65535
- Monotonically increasing during normal operation

**Anomaly signals:**

| CycleCounter Pattern | Delta | Likely Cause |
|---|---|---|
| Sequential: 100 → 101 → 102 | +1 | Normal |
| Gap: 100 → 101 → 106 | +5 | Dropped frames |
| Duplicate: 100 → 101 → 101 | 0 | Replay attack |
| Jump: 100 → 101 → 850 | +749 | Spoofed frame |
| Reset: 100 → 101 → 0 | negative | Device restart or spoofed |

**IDS feature:** `cycle_counter_delta` — the difference between consecutive
CycleCounter values. Normal value = 1. Any deviation triggers investigation.

---

#### DataStatus (Byte 18, 1 byte)

DataStatus describes the state of the process data being sent.
It answers: is this data valid? Is the device operating correctly?
Can this data be trusted for control decisions?

**Typical normal value: `0x35`**

Bit-level breakdown of `0x35` (binary: `0011 0101`):

| Bit | Name | Value in 0x35 | Meaning |
|---|---|---|---|
| Bit 7 | Ignore | 0 | Receiver should process this frame |
| Bit 6 | DataValid | 1 | Process data is valid and usable |
| Bit 5 | Reserved | 0 | — |
| Bit 4 | ProviderState | 1 | Provider (IO Controller) is running |
| Bit 3 | Reserved | 0 | — |
| Bit 2 | StationProblemIndicator | 1 | No station problem |
| Bit 1 | Reserved | 0 | — |
| Bit 0 | PrimaryAR | 1 | This is the primary application relationship |

**Key insight from Day 2 study:** Network communication can appear
completely normal (FrameID correct, CycleCounter sequential) while
DataStatus indicates invalid process data. This means the network is
healthy but the process itself is in a fault state. An IDS that only
checks timing and sequence numbers would miss this.

**IDS relevance:**
- DataStatus changing from `0x35` to an unexpected value mid-session
  indicates device state change — could be device fault or attack
- DataValid bit (Bit 6) flipping to 0 → data should not be used for
  control, but a malicious frame might keep it at 1 while sending
  corrupted payload data

---

#### TransferStatus (Byte 19, 1 byte)

TransferStatus indicates the health of the communication transfer itself.
It answers: was this communication successful? Is the communication path
healthy?

| Value | Meaning |
|---|---|
| `0x00` | Transfer valid — data delivered successfully |
| Non-zero | Transfer problem — communication path issue |

**IDS relevance:**
- TransferStatus `!= 0x00` → communication health problem
- Malformed frames may carry incorrect TransferStatus values

---

### Process Data Payload (Bytes 20+)

- Contains the actual cyclic IO data — sensor readings, actuator commands
- Length is fixed per application and configured at system startup
- Does not change during normal operation for a given IO connection
- Content is application-specific — zeros in simulation represent no
  real PLC attached

**IDS relevance:**
- Payload length changing mid-session → malformed frame
- Payload length inconsistent with established FrameID baseline → anomaly

---

## Field Importance Ranking for Anomaly Detection

Ranked by detection value for the three attack types this project targets:

```
Rank 1 — CycleCounter
  Detects: replay attacks, missing frames, timing anomalies
  Feature: cycle_counter_delta

Rank 2 — FrameID
  Detects: unknown communication, unexpected devices, protocol abuse
  Feature: frame_id_value, frame_id_is_known

Rank 3 — DataStatus
  Detects: device state changes, invalid process data
  Feature: data_status_value, data_valid_bit

Rank 4 — TransferStatus
  Detects: communication health issues, transfer problems
  Feature: transfer_status_value
```

---

## How Wireshark Parses PROFINET Frames

Wireshark reads Ethernet frames byte by byte using its dissector system.
The PROFINET RT dissector is implemented in `packet-pn-rt.c`.

**Parsing sequence:**
```
Read bytes 12–13 → check EtherType
If EtherType == 0x8892 → hand off to PROFINET RT dissector
    Read bytes 14–15 → FrameID
    Read bytes 16–17 → CycleCounter
    Read byte 18     → DataStatus
    Read byte 19     → TransferStatus
    Remaining bytes  → Process Data
```

**Study note:** The dissector source was cloned from
`github.com/wireshark/wireshark` for study. The file was large and
initially overwhelming. The key insight for reading it: focus on
the `hf_` field definitions at the top of the file — these define
every named field with its offset, length, and display format. The
parsing logic in the functions below confirms how those fields are
extracted from the raw bytes.

Key field definitions found in `packet-pn-rt.c`:
```c
static int hf_pn_rt_frame_id
static int hf_pn_rt_cycle_counter
static int hf_pn_rt_data_status
static int hf_pn_rt_transfer_status
```

---

## Hex Decoding Reference

To manually decode a PROFINET field value from hex:

**Example: FrameID bytes = `80 01`**
```
0x80 = 8 × 16¹ + 0 × 16⁰ = 128
0x01 = 0 × 16¹ + 1 × 16⁰ = 1
Combined as big-endian: 0x8001 = (128 × 256) + 1 = 32769 decimal
```

**Example: CycleCounter bytes = `00 65`**
```
0x00 = 0
0x65 = 6 × 16¹ + 5 × 16⁰ = 101
Combined: 0x0065 = (0 × 256) + 101 = 101 decimal
→ This frame is cycle number 101
```

---

## Summary — What Makes a Frame "Normal"

| Field | Normal Value | Anomaly Signal |
|---|---|---|
| EtherType | `0x8892` | Any other value |
| FrameID | `0x8000–0xBFFF`, constant per session | Out of range or changed mid-session |
| CycleCounter delta | +1 each frame | 0 (replay), >1 (drop), jump (spoof) |
| DataStatus | `0x35` during operation | Unexpected value change |
| TransferStatus | `0x00` | Non-zero value |
| Source MAC | Fixed per IO Controller | New or changed MAC |
| Frame length | Fixed per application | Length change mid-session |

---

## Sources

- Wireshark dissector source: `github.com/wireshark/wireshark/blob/master/epan/dissectors/packet-pn-rt.c`
- See `protocol_notes/sources.md` for full source list and methodology notes
