# Day 1 — Week 3 — PROFINET Fundamentals

**Date:** 12/06/2026  
**Hours Logged:** 2.5 Hours  
**Focus:** Understanding PROFINET Architecture, Communication Model, and Security Relevance

---

# Objective

- Understand what PROFINET is and why it is used in industrial environments.
- Learn the role of IO Controllers, IO Devices, and IO Supervisors.
- Understand why PROFINET RT avoids TCP for real-time communication.
- Study EtherType, FrameID, and CycleCounter.
- Identify protocol fields that can later be used for anomaly detection.

---

# What is PROFINET

## Definition

- PROFINET (Process Field Network) is an Industrial Ethernet communication protocol used in automation systems.
- It enables communication between controllers and field devices such as sensors, actuators, motor drives, and robots.
- PROFINET is designed for deterministic and real-time industrial communication.

## Why PROFINET Exists

Traditional office networks prioritize:

- Reliability
- Correctness
- Data integrity

Industrial networks prioritize:

- Deterministic timing
- Predictable communication
- Fast response times

### Example

```text
Office Network:
Open Website
↓
200 ms delay acceptable

Industrial Network:
Emergency Stop Signal
↓
200 ms delay may be dangerous
```

## Key Insight

> Office Networks prioritize Reliability and Correctness.
>
> Industrial Networks prioritize Determinism and Timing.

---

# PROFINET Components

## IO Controller

### Definition

- The IO Controller is responsible for controlling the automation process.
- It acts as the decision-making component of the system.

### Typical Device

- PLC (Programmable Logic Controller)

### Responsibilities

- Receives sensor data
- Executes control logic
- Sends commands to field devices
- Controls industrial processes

### Example

```text
Temperature Sensor
        ↓
       PLC
        ↓
   Cooling Fan
```

The PLC decides when the fan should be turned ON or OFF.

---

## IO Device

### Definition

- IO Devices interact directly with the physical process.

### Examples

- Sensors
- Actuators
- Motor Drives
- Valves
- Robots

### Responsibilities

- Provide process data
- Receive control commands
- Execute physical actions

---

## IO Supervisor

### Definition

- The IO Supervisor performs monitoring, diagnostics, and configuration.

### Examples

- Engineering Workstation
- Siemens TIA Portal
- Maintenance Laptop

### Responsibilities

- Configure devices
- Upload PLC programs
- Monitor network status
- Perform diagnostics

---

# Why PROFINET RT Does Not Use TCP

## Problem with TCP

TCP provides:

- Acknowledgements (ACKs)
- Retransmissions
- Flow Control
- Congestion Control
- Connection Management

These mechanisms improve reliability but introduce:

- Latency
- Jitter
- Unpredictable timing

## Industrial Requirement

Industrial systems require:

**Deterministic Communication**

### Example

```text
PLC
↓
Robot Arm

Position Update Every 1 ms
```

If packet 12 is lost:

```text
TCP:
Wait
↓
Retransmit Packet 12
↓
Delay Packet 13 and 14
```

The robot arm is interested in:

```text
Latest Position
```

not

```text
Perfect Historical Accuracy
```

## Key Insight

> Missing one update is often less harmful than delaying future updates.

## Result

PROFINET RT communicates directly over Ethernet and avoids TCP and UDP for real-time process data.

### PROFINET RT Stack

```text
Ethernet
↓
PROFINET RT
```

### Traditional IT Stack

```text
Ethernet
↓
IP
↓
TCP
↓
Application
```

---

# EtherType

## What is EtherType?

- EtherType is a field inside the Ethernet header.
- It tells the receiving device what protocol follows the Ethernet header.

Without EtherType:

```text
Ethernet Header
↓
Unknown Payload
```

The receiver would not know which protocol parser to use.

## Common EtherType Values

| EtherType | Protocol |
|------------|------------|
| 0x0800 | IPv4 |
| 0x86DD | IPv6 |
| 0x0806 | ARP |
| 0x8892 | PROFINET RT |

## EtherType 0x8892

When a device sees:

```text
EtherType = 0x8892
```

it knows:

```text
Ethernet
↓
PROFINET RT
```

follows next.

## Performance Benefits

### Traditional TCP Communication

```text
Ethernet
↓
IP
↓
TCP
↓
Application
```

Requires:

- Header Parsing
- Validation
- State Tracking
- ACK Processing
- Retransmission Logic

### PROFINET RT Communication

```text
Ethernet
↓
PROFINET RT
↓
Process Data
```

Benefits:

- Lower Latency
- Lower Jitter
- More Predictable Timing

---

# FrameID

## Problem

PROFINET RT does not use:

- TCP
- UDP
- Port Numbers

Therefore, the receiver needs another method to identify communication streams.

## Solution

FrameID identifies the purpose of a PROFINET communication stream.

Think of FrameID as:

- Application Identifier
- Conversation Identifier

within PROFINET.

## Example

PLC communicating with:

```text
Temperature Sensor
Motor Drive
Emergency Stop Module
```

FrameID helps distinguish:

```text
Temperature Data
Motor Commands
Emergency Stop Data
```

## Important Note

FrameID does **NOT** identify individual packets.

FrameID identifies:

```text
Type of Communication
```

## IDS Relevance

Potential anomalies include:

- Unknown FrameID
- Missing FrameID
- Unexpected FrameID frequency
- New FrameID appearing in established traffic

---

# CycleCounter

## Problem

PROFINET RT does not use TCP sequence numbers.

The receiver still needs to know:

- Is this the newest update?
- Was an update missed?
- Was a frame duplicated?

## Solution

PROFINET uses CycleCounter.

CycleCounter acts as:

```text
Cycle Number
```

for cyclic communication.

## Example

### Normal Communication

```text
100
101
102
103
104
105
```

### Missing Cycles

```text
100
101
102
106
107
```

Missing:

```text
103
104
105
```

### Duplicate Cycles

```text
100
101
102
102
103
```

## Temporal Consistency

CycleCounter helps determine:

```text
Is communication occurring exactly as expected?
```

This property is called:

**Temporal Consistency**

## Why CycleCounter Is Valuable

FrameID tells us:

```text
WHAT communication this is.
```

CycleCounter tells us:

```text
WHETHER communication is behaving normally.
```

## IDS Relevance

Potential anomalies:

- Missing Cycles
- Duplicate Cycles
- Repeated Values
- Counter Jumps
- Unexpected Resets

---

# Security Observations

## Observation 1 — Anomaly ≠ Attack

An anomaly indicates:

```text
Behavior differs from established baseline.
```

An anomaly may be caused by:

- Attack
- Device Failure
- Network Issue
- Maintenance Activity
- Configuration Change

Therefore:

```text
Anomaly = Investigation Required
```

not

```text
Attack Confirmed
```

---

## Observation 2 — Engineering Workstations Are High-Value Targets

Compromising an engineering workstation may allow attackers to:

- Modify PLC Logic
- Reconfigure Devices
- Upload Malicious Programs
- Change Process Parameters

without directly attacking the PLC.

---

## Observation 3 — Valid Packets ≠ Safe Operations

In industrial environments:

```text
Valid Network Traffic
```

does not always mean:

```text
Safe Physical Behavior
```

Commands may be technically valid but operationally dangerous.

---

## Observation 4 — Late Data Can Be More Dangerous Than Missing Data

Industrial systems depend on predictable timing.

A delayed update may cause:

- Incorrect Decisions
- Process Instability
- Equipment Damage
- Safety Risks

---

# Project Connections

## Future IDS Features

### Timing Features

- Cycle Time
- Frames Per Second
- Cycle Time Variance
- Inter-Packet Timing

### Protocol Features

- FrameID
- FrameID Frequency
- Unknown FrameID Count
- Missing FrameID Count

### Integrity Features

- Missing CycleCounter Count
- Duplicate CycleCounter Count
- CycleCounter Jumps
- Unexpected Counter Resets

---

# Key Takeaways

1. PROFINET is an Industrial Ethernet protocol designed for deterministic communication.
2. Industrial systems prioritize timing and predictability over perfect reliability.
3. PROFINET RT avoids TCP to reduce latency and jitter.
4. EtherType 0x8892 identifies PROFINET RT traffic.
5. FrameID identifies the purpose of a communication stream.
6. CycleCounter helps detect missing, duplicated, or abnormal communication cycles.
7. Industrial IDS design focuses heavily on timing, consistency, and baseline behavior.
8. Anomaly detection does not automatically imply an attack.




# Day 2 — Week 3 — PROFINET Fundamentals

**Date:** 17/06/2026  
**Hours Logged:** 2.5 Hours  
**Focus:** Understanding fields inside PROFINET RT frame

---


# PROFINET RT Frame Layout


### Ethernet header
- Divided into Destination MAC, Source MAC and EtherType (0x8892)

### PROFINET RT header
- Divided into FrameID, CycleCounter, DataStatus, TransferStatus

### Payload
- Process Data


```text
Offset    Length    Field
--------------------------------
0         6         Destination MAC
6         6         Source MAC
12        2         EtherType
14        2         FrameID
16        2         CycleCounter

```


## How Wireshark parses packets

- While parsing packets, Wireshark reads byte by byte to understand which field is at what number

```text

Read bytes 0-5
→ Destination MAC

Read bytes 6-11
→ Source MAC

Read bytes 12-13
→ EtherType

Read bytes 14-15
→ FrameID


```



# Decoding hex manually

###Q] How to decode 0x0065 in decimal?

- 0x means the number is hexadecimal (Base 16)
- To convert break it into individual number and multiple by 16 to the power digits on right.
- Then add all results to get the decimal value




# DataStatus and TransferStatus fields in PROFINET 

- DataStatus describes the state of the process data. It helps answer whether the data is valid, is the device in a good state, can the data be trusted?

- If DataStatus suddenly changes, it can indicated valid data turning invalid. PLC might ignore data, raise alarm or enter safe mode



- TransferStatus indicates the state of the communication transfer
- It helps answer whether the communication was successful, is the sender operating normally, is the communication path healthy?




# Field importance ranking

- Ranking fields for anomaly detection:
```text
1. CycleCounter
2. FrameID
3. DataStatus
4. TransferStatus


Reason:

CycleCounter
Most useful for:

Missing Frames
Duplicate Frames
Timing Anomalies
Replay Detection


FrameID
Most useful for:

Unknown Communication
Unexpected Devices
Protocol Abuse


DataStatus
Most useful for:

Device State Changes
Invalid Process Data


TransferStatus
Most useful for:

Communication Health
Transfer Problems


```




# Wireshark Dissector study



- Cloned the https://github.com/wireshark/wireshark.git repository to get the packet-pn-rt.c file to understand PROFINET frame structure

- This file tells you how wireshark parse PROFINET RT frames




# What surprised me

- Communication normal is not always equal to Healthy process. 
- FrameID and cycleCount might indicate normal values but DataStatus might indicate Invalid. Meaning the network is working but the process is not



# Problems I faced

-  After opening the wireshark dissector i got overwhelmed by the amount of file and contents in it.
- Same thing happened when i opened the packet-pn-rt.c file. Was unable to understand and extract required fields for my studies. 
- Solved this problem by understanding how wireshark works internally. Used web search and chatgpt for the same and then extracted the required fields




## Limitation

Official PROFINET IO Base Specification unavailable.

Field semantics studied using:
- Wireshark dissector analysis
- Public PROFINET documentation
- Protocol reasoning

Exact field ranges and some implementation-specific details will be verified later using captured PROFINET traffic.

