# PROFINET Protocol — Overview

## What is PROFINET

PROFINET (Process Field Network) is an Industrial Ethernet communication
protocol used in automation systems. It enables communication between
controllers and field devices such as sensors, actuators, motor drives,
and robots. PROFINET is designed for deterministic and real-time
industrial communication.

---

## Why PROFINET Exists

Traditional office networks and industrial networks have fundamentally
different priorities:

| Property | Office Network | Industrial Network |
|---|---|---|
| Primary goal | Reliability and correctness | Deterministic timing |
| Latency tolerance | High — 200ms acceptable | Very low — 1ms required |
| Missing data | Retransmit and recover | Skip and use next update |
| Timing variance | Acceptable | Dangerous |

**Key insight:** Office networks prioritize reliability and correctness.
Industrial networks prioritize determinism and timing. A 200ms delay
opening a webpage is inconvenient. A 200ms delay on an emergency stop
signal can cause equipment damage or injury.

---

## PROFINET Components

### IO Controller
- The decision-making component of the automation system
- Typical device: PLC (Programmable Logic Controller)
- Receives sensor data, executes control logic, sends commands to field devices
- Example: A PLC reads temperature sensor data and decides when to activate
  a cooling fan

### IO Device
- Interacts directly with the physical process
- Examples: sensors, actuators, motor drives, valves, robots
- Provides process data to the IO Controller and executes physical actions
  based on received commands

### IO Supervisor
- Performs monitoring, diagnostics, and configuration
- Examples: engineering workstations, Siemens TIA Portal, maintenance laptops
- Does not participate in real-time cyclic communication — operates
  at a separate, lower priority

---

## Why PROFINET RT Does Not Use TCP

TCP provides acknowledgements, retransmissions, flow control, and
connection management. These mechanisms improve reliability but introduce
latency, jitter, and unpredictable timing — exactly what industrial
systems cannot tolerate.

### The Core Problem with TCP in Industrial Systems

Consider a PLC sending position updates to a robot arm every 1ms:

```
Normal cyclic communication:
Frame 10 → Frame 11 → Frame 12 → Frame 13 → Frame 14

If Frame 12 is lost over TCP:
Frame 10 → Frame 11 → [wait] → [retransmit 12] → Frame 13 delayed
```

The robot arm needs the **latest position**, not a historically complete
sequence. Delaying Frame 13 and 14 while waiting for a retransmission
of Frame 12 is worse than simply missing Frame 12.

**Key insight:** In industrial systems, missing one update is often less
harmful than delaying all future updates.

### PROFINET RT Stack vs Traditional IT Stack

```
PROFINET RT:          Traditional IT:
Ethernet              Ethernet
    ↓                     ↓
PROFINET RT               IP
    ↓                     ↓
Process Data              TCP
                          ↓
                      Application
```

By removing IP and TCP, PROFINET RT eliminates header parsing overhead,
retransmission logic, connection state tracking, and ACK processing —
resulting in lower latency and deterministic timing.

---

## EtherType 0x8892

EtherType is a 2-byte field inside the Ethernet header at bytes 12–13.
It tells the receiving device what protocol follows the Ethernet header.

| EtherType | Protocol |
|---|---|
| 0x0800 | IPv4 |
| 0x86DD | IPv6 |
| 0x0806 | ARP |
| 0x8892 | PROFINET RT |

When a device sees `EtherType = 0x8892`, it knows to parse the following
bytes as a PROFINET RT frame rather than an IP packet. This is the first
field checked by the Wireshark PROFINET dissector (`packet-pn-rt.c`) to
identify PROFINET traffic.

**IDS relevance:** Any frame with `EtherType = 0x8892` must be inspected
by the IDS. Any frame that bypasses this filter could indicate protocol
abuse or a misconfigured device.

---

## FrameID

PROFINET RT does not use TCP, UDP, or port numbers. FrameID solves the
resulting identification problem — it tells the receiver what type of
communication this frame carries.

- FrameID acts as an application-layer identifier within PROFINET
- One PLC communicating with multiple devices uses different FrameIDs
  for each communication stream (temperature data, motor commands,
  emergency stop data)
- FrameID identifies the **type** of communication, not individual packets

### FrameID Ranges

| Range | Class | Meaning |
|---|---|---|
| 0x0020–0x007F | RT Class 3 IRT | Isochronous real-time |
| 0x8000–0xBFFF | RT Class 1/2/3 | Standard real-time cyclic |
| 0xC000–0xFBFF | Acyclic RT | Alarms and events |

### IDS Relevance
- Unknown FrameID appearing in established traffic → potential protocol abuse
- New FrameID not seen during baseline period → unexpected device or connection
- Unexpected FrameID frequency → timing anomaly

---

## CycleCounter

PROFINET RT does not use TCP sequence numbers. CycleCounter fills this
role — it gives the receiver a way to detect missing, duplicated, or
out-of-order frames.

### Normal CycleCounter Behavior
```
Frame 1: CycleCounter = 100
Frame 2: CycleCounter = 101
Frame 3: CycleCounter = 102
Frame 4: CycleCounter = 103
```

### Anomalous Patterns

| Pattern | Example | Meaning |
|---|---|---|
| Missing cycles | 100, 101, 106 | Frames dropped or filtered |
| Duplicate cycles | 100, 101, 101 | Replay attack or retransmission |
| Counter jump | 100, 101, 850 | Spoofed frame from different session |
| Unexpected reset | 100, 101, 0 | Device restart or spoofed frame |

CycleCounter provides **temporal consistency** — the ability to verify
that communication is occurring exactly as expected, at the expected rate,
with no gaps or repetitions.

---

## Security Observations

### Anomaly ≠ Attack
An anomaly indicates behavior that differs from the established baseline.
The cause may be an attack, device failure, network issue, maintenance
activity, or configuration change. An anomaly requires investigation —
it does not confirm an attack.

### Engineering Workstations Are High-Value Targets
Compromising an engineering workstation may allow an attacker to modify
PLC logic, reconfigure devices, or upload malicious programs without
ever sending anomalous network traffic — because all commands arrive
through legitimate channels.

### Valid Packets ≠ Safe Operations
Technically valid PROFINET frames can carry operationally dangerous
commands. Network-layer IDS can detect structural anomalies but cannot
validate whether process commands are physically safe.

### Late Data Can Be More Dangerous Than Missing Data
Industrial systems depend on predictable timing. A delayed control update
can cause incorrect decisions, process instability, equipment damage,
or safety risks. This is why timing features are the most important
features in this IDS design.

---

## IDS Feature Map

| Feature Category | Specific Feature | What it Detects |
|---|---|---|
| Timing | Inter-arrival time (IAT) mean | Cycle rate changes |
| Timing | IAT variance | Timing jitter anomalies |
| Timing | Frames per second | Flood or suppression attacks |
| Protocol | FrameID value | Unknown communication streams |
| Protocol | FrameID frequency | Unexpected frame rate per stream |
| Integrity | CycleCounter delta | Replay, missing, out-of-order frames |
| Integrity | CycleCounter jump magnitude | Spoofed frames from other sessions |
| State | DataStatus value | Device state changes |
| State | TransferStatus value | Communication health changes |

---

## Sources

- Wireshark PROFINET dissector: `github.com/wireshark/wireshark` → `packet-pn-rt.c`
- CISA ICS advisories: `cisa.gov/ics-advisories` (search PROFINET)
- See `protocol_notes/sources.md` for full source list
