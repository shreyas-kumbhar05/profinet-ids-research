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




# Day 3 — Week 3 — Building a Minimal PROFINET RT Frame

**Date:** 23/06/2026  
**Hours Logged:** 3 Hours  
**Focus:** Constructing, Inspecting, and Validating a Minimal PROFINET RT Ethernet Frame

---

# Objective

The objective of Day 3 was to move from protocol theory to protocol construction.

Previous days focused on:

```text
PROFINET Architecture
↓
Frame Structure
↓
Frame Fields
↓
IDS-Relevant Metadata
```

Day 3 focused on:

```text
Protocol Knowledge
↓
Frame Construction
↓
Frame Inspection
↓
Frame Validation
```

The goal was to manually construct a valid PROFINET RT frame and understand how each protocol field appears in raw Ethernet traffic.

---

# Research Motivation

Industrial Intrusion Detection Systems ultimately operate on packets captured from the network.

Before analyzing industrial traffic, it is necessary to understand:

- How a valid PROFINET RT frame is structured
- Which fields appear in the frame
- How protocol parsers interpret those fields
- How abnormal values might be detected

Building a frame manually provides a deeper understanding than only observing traffic in Wireshark.

---

# PROFINET RT Frame Construction

A minimal PROFINET RT frame was implemented using Scapy and Python.

The generated frame contains:

```text
Ethernet Header
↓
PROFINET RT Header
↓
Simulated Cyclic IO Data
```

---

## Ethernet Header

The Ethernet header contains:

| Field | Size |
|---------|---------|
| Destination MAC | 6 Bytes |
| Source MAC | 6 Bytes |
| EtherType | 2 Bytes |

EtherType was set to:

```text
0x8892
```

which identifies the frame as PROFINET RT traffic.

---

## PROFINET RT Header

The custom PROFINET RT header contains:

| Field | Size |
|---------|---------|
| FrameID | 2 Bytes |
| CycleCounter | 2 Bytes |
| DataStatus | 1 Byte |
| TransferStatus | 1 Byte |

Total header size:

```text
2 + 2 + 1 + 1 = 6 Bytes
```

---

## Cyclic IO Payload

The frame includes a simulated IO payload.

```python
bytes(payload_size)
```

was used to generate zero-filled process data.

This payload does not represent a real PLC process image.

Instead, it serves as placeholder cyclic data so that the generated frame resembles real industrial traffic.

---

# Header Field Selection

## FrameID

Selected value:

```text
0x8001
```

Reason:

- Falls inside the valid RT communication range.
- Represents cyclic real-time communication.
- Suitable for testing and packet inspection.

---

## CycleCounter

Initial value:

```text
0
```

Reason:

- Simplifies debugging.
- Future traffic generators can increment the value automatically.

---

## DataStatus

Selected value:

```text
0x35
```

Reason:

- Represents valid operational process data.
- Provides a realistic starting point for frame construction.

---

## TransferStatus

Selected value:

```text
0x00
```

Reason:

- Indicates successful transfer state.
- Simplifies validation testing.

---

# Frame Inspection

A dedicated inspection function was implemented.

The purpose of this function is to:

- Extract protocol fields from raw packet bytes
- Decode values into human-readable form
- Verify that construction logic matches protocol expectations

Displayed information includes:

- Source MAC
- Destination MAC
- EtherType
- FrameID
- CycleCounter
- DataStatus
- TransferStatus
- Frame Length

The frame is additionally displayed as a hexadecimal dump.

---

# Understanding Raw Packet Bytes

The generated frame produced the following initial bytes:

```text
01 0e cf 00 00 00
08 00 27 a0 f4 9c
88 92
80 01
00 00
35
00
```

These correspond to:

```text
Destination MAC
Source MAC
EtherType
FrameID
CycleCounter
DataStatus
TransferStatus
```

This demonstrates that protocol fields are ultimately represented as raw bytes and that Wireshark reconstructs protocol information by parsing those bytes according to protocol definitions.

---

# Frame Validation

A validation stage was implemented before transmission.

Validation checks included:

- EtherType correctness
- Minimum payload length
- Valid FrameID range
- TransferStatus correctness
- PROFINET multicast destination

Example output:

```text
[PASS] EtherType is 0x8892
[PASS] Payload >= 6 bytes
[PASS] FrameID in RT range
[PASS] TransferStatus is 0x00
[PASS] Dst MAC is PROFINET multicast
```

This step ensures that malformed frames are detected before traffic generation.

---

# IDS Perspective

Several fields created during frame construction are directly relevant to anomaly detection.

## FrameID

Potential indicators:

- Unknown FrameID
- Unexpected FrameID appearance
- Missing expected FrameIDs

---

## CycleCounter

Potential indicators:

- Missing cycles
- Duplicate cycles
- Replay attacks
- Unexpected resets

---

## DataStatus

Potential indicators:

- Device faults
- Invalid process data
- Unexpected operational state changes

---

## TransferStatus

Potential indicators:

- Communication degradation
- Transfer failures
- Protocol state changes

---

# Key Technical Insight

A PROFINET RT frame is fundamentally:

```text
Ethernet
+
Protocol Metadata
+
Process Data
```

The protocol metadata is relatively small compared to the process payload, yet those few bytes contain most of the information required for protocol analysis and anomaly detection.

---

# Connection to Week 4

This implementation becomes the foundation of the future traffic generator.

Planned evolution:

```text
Static Frame
↓
Repeated Transmission
↓
Incrementing CycleCounter
↓
Traffic Generation
↓
Baseline Industrial Dataset
```

The `build_profinet_rt_frame()` function will be reused by future generators to create realistic cyclic industrial traffic for IDS research.

---

# Key Takeaways

1. A valid PROFINET RT frame can be manually constructed using Scapy.
2. EtherType 0x8892 identifies PROFINET RT traffic at Layer 2.
3. FrameID, CycleCounter, DataStatus, and TransferStatus form the core protocol metadata.
4. Raw packet bytes directly correspond to protocol fields observed in Wireshark.
5. Validation is necessary before traffic generation.
6. Protocol metadata provides valuable features for future anomaly detection models.
7. This frame constructor forms the basis for future industrial traffic simulation and IDS dataset generation.





# Day 4 — Week 3 — Frame Annotation and Protocol Feature Engineering

**Date:** 04/07/2026  
**Hours Logged:** 3 Hours  
**Focus:** Annotating every byte of a PROFINET RT frame and connecting protocol fields to future IDS features.

---

# Objective

The objective of Day 4 was to move from simply understanding the PROFINET protocol to understanding every transmitted byte and documenting how each field contributes to industrial anomaly detection.

Rather than viewing a packet as raw hexadecimal values, the goal was to interpret every byte as protocol information that can later become a measurable feature for machine learning.

---

# Research Motivation

- Byte-level protocol understanding is essential before attempting protocol-aware IDS development.
- Every protocol field represents meaningful industrial information rather than arbitrary data.
- Statistical baseline features used by machine learning originate directly from protocol fields.
- A protocol engineer should be capable of interpreting a hex dump without relying entirely on Wireshark.

---

# Understanding the Purpose of `frame_annotation.md`

A hexadecimal dump initially appears as a sequence of bytes:

```text
01 0e cf 00 00 00
08 00 27 a0 f4 9c
88 92
80 01
00 00
35
00
```

The purpose of `frame_annotation.md` is to translate those bytes into protocol meaning.

Every frame should be decomposed into:

- Destination MAC
- Source MAC
- EtherType
- FrameID
- CycleCounter
- DataStatus
- TransferStatus
- Cyclic IO Data

This document serves as evidence of protocol-level understanding and provides a foundation for future protocol analysis.

---

# Understanding the Ethernet Layer

The Ethernet header answers three fundamental questions.

```text
Who transmitted the frame?
↓

Source MAC

Who should receive it?
↓

Destination MAC

Which protocol follows?
↓

EtherType
```

Unlike conventional enterprise traffic, PROFINET RT relies directly on Ethernet. Consequently, the Ethernet header becomes significantly more important because no IP or TCP layer exists between Ethernet and the industrial protocol.

---

# Understanding the PROFINET RT Header

Immediately after the Ethernet header, six bytes define the PROFINET RT header.

```text
80 01
00 00
35
00
```

These bytes represent:

```text
FrameID
↓

CycleCounter
↓

DataStatus
↓

TransferStatus
```

Each field describes a different aspect of industrial communication.

- FrameID identifies the communication stream.
- CycleCounter describes temporal behaviour.
- DataStatus describes process validity.
- TransferStatus describes communication health.

---

# FrameID as a Semantic Feature

FrameID was deliberately selected as `0x8001` because it lies within the valid RT communication range while remaining easy to recognize during debugging.

FrameID does not identify individual packets.

Instead, it identifies the communication stream or service associated with the frame.

Unexpected FrameIDs may indicate:

- Unknown communication
- Protocol misuse
- Configuration changes
- Malformed frames

---

# CycleCounter as a Temporal Feature

CycleCounter represents communication sequence rather than process data.

Under normal operation:

```text
0
↓

1
↓

2
↓

3
↓

4
```

Possible anomalies include:

- Duplicate values
- Missing values
- Counter jumps
- Counter resets

These temporal characteristics make CycleCounter one of the most valuable protocol fields for anomaly detection.

---

# Research Insight

Industrial IDS systems rarely depend upon a single protocol field.

Instead, multiple categories of features are combined.

```text
Semantic Features
+

Temporal Features
+

Statistical Features
↓

Industrial Anomaly Detection
```

Examples include:

Semantic Features

- FrameID
- EtherType

Temporal Features

- CycleCounter
- Inter-arrival Time

Statistical Features

- EtherType frequency
- FrameID frequency
- CycleCounter distribution
- Timing variance

---

# Important Observation

Every protocol field serves a different engineering purpose.

| Field | Purpose |
|--------|----------|
| Source MAC | Device Identity |
| Destination MAC | Communication Target |
| EtherType | Protocol Identification |
| FrameID | Communication Type |
| CycleCounter | Temporal Consistency |
| DataStatus | Process State |
| TransferStatus | Communication Health |

An industrial IDS gains significantly more accuracy by correlating these independent protocol features rather than analysing a single field in isolation.

---

# Connection to Future Work

The protocol fields documented today will become direct inputs to the future feature extraction pipeline.

Examples include:

- Known Source MAC verification
- Unexpected EtherType detection
- FrameID validation
- CycleCounter delta calculation
- DataStatus monitoring
- TransferStatus validation
- Timing feature extraction

These protocol-aware features will later be used by statistical methods and machine learning models to distinguish normal industrial communication from anomalous behaviour.

---

# Key Insight

Understanding a protocol means understanding every transmitted byte, why that byte exists, what engineering problem it solves, and how it can later be transformed into a measurable feature for anomaly detection.



---


# Day 5 — Week 3 — Statistical Baseline for PROFINET RT Communication

**Date:** 07/07/2026  
**Hours Logged:** 2.5 Hours  
**Focus:** Understanding cyclic communication, timing behaviour, statistical baseline modelling, and feature engineering for Industrial Intrusion Detection Systems (IDS).

---

# Objective

The objective of today's study was to understand how deterministic communication in PROFINET RT enables statistical anomaly detection. Rather than analysing individual protocol fields alone, the focus shifted towards modelling communication behaviour over time and identifying which statistical properties can later be transformed into machine learning features.

---

# From Protocol Analysis to Statistical Analysis

During the previous days, the protocol was studied at the frame level.

```text
Ethernet
        ↓
PROFINET RT Header
        ↓
FrameID
CycleCounter
DataStatus
TransferStatus
```

Today's focus expanded beyond individual packets.

Instead of asking:

> "What does this packet contain?"

the question becomes:

> "Is this packet behaving consistently with the communication pattern observed over hundreds or thousands of previous packets?"

This transition marks the beginning of feature engineering for anomaly detection.

---

# Understanding Cyclic Communication

Unlike traditional enterprise networks where communication occurs only when requested, PROFINET RT continuously exchanges process data at predefined time intervals.

```text
IO Controller
        ↓
IO Device
        ↓
IO Controller
        ↓
IO Device
        ↓
Repeat
```

The communication continues throughout system operation regardless of user interaction.

This deterministic behaviour creates highly predictable network traffic that is particularly suitable for statistical anomaly detection.

---

# Why 4 ms Was Selected

Although PROFINET supports communication cycles as low as 1 ms, this project adopts a 4 ms communication cycle.

Reasons include:

- Represents a realistic industrial deployment.
- Produces approximately 250 frames per second.
- Reduces CPU overhead during software-based traffic generation.
- Produces manageable dataset sizes.
- Maintains sufficient temporal resolution for anomaly detection experiments.

The selected cycle therefore balances realism, computational efficiency, and experimental reproducibility.

---

# Understanding Inter-Arrival Time (IAT)

Inter-Arrival Time (IAT) represents the elapsed time between two consecutive packets.

Example:

```text
Frame Arrival Times

0 ms
4 ms
8 ms
12 ms
16 ms

↓

Inter-Arrival Time

4 ms
4 ms
4 ms
4 ms
```

Instead of learning absolute timestamps, an Industrial IDS learns the statistical distribution of these timing differences.

When communication timing changes unexpectedly,

```text
4 ms
4 ms
8 ms
4 ms
```

the deviation may indicate:

- Network congestion
- Device processing delay
- Switch buffering
- Packet loss
- Denial-of-Service
- Man-in-the-Middle forwarding delay
- Frame injection

An abnormal IAT therefore represents an anomaly requiring investigation rather than direct evidence of an attack.

---

# Understanding Jitter

Real industrial communication is deterministic but never perfectly periodic.

Small timing variations naturally occur because of:

- Operating system scheduling
- Network interface processing
- Ethernet switch forwarding delay
- Hardware clock inaccuracies
- Buffering delays

These small timing variations are collectively referred to as **jitter**.

Consequently, realistic industrial communication should exhibit low but non-zero timing variation.

---

# Gaussian Jitter

The traffic generator models realistic communication timing using a Gaussian distribution.

```python
random.gauss(4.0, 0.3)
```

where:

- Mean = 4.0 ms
- Standard deviation = 0.3 ms

This produces timing values concentrated around the expected communication cycle while preserving realistic timing variation.

Example:

```text
3.97 ms
4.03 ms
3.99 ms
4.05 ms
4.01 ms
```

Compared to perfectly periodic communication:

```text
4.00 ms
4.00 ms
4.00 ms
4.00 ms
```

Gaussian jitter produces traffic that more closely resembles real industrial deployments.

---

# Statistical Baseline

Industrial IDS does not learn individual packets.

Instead, it learns the statistical characteristics of normal communication.

Examples include:

| Feature | Expected Behaviour |
|----------|-------------------|
| Mean IAT | Approximately 4 ms |
| IAT Standard Deviation | Low |
| Frame Length | Constant |
| Source MAC | Fixed |
| Destination MAC | Fixed |
| FrameID | Stable |
| CycleCounter Delta | +1 |
| DataStatus | Stable |

These measurements collectively define the normal communication baseline.

Future observations are compared against this baseline to determine whether communication remains consistent with expected industrial behaviour.

---

# Feature Categories for Industrial IDS

The protocol fields studied throughout Week 3 naturally form several feature categories.

## Identity Features

- Source MAC
- Destination MAC

Purpose:

Verify that communication originates from expected industrial devices.

---

## Semantic Features

- EtherType
- FrameID

Purpose:

Describe the protocol and communication purpose.

---

## Temporal Features

- CycleCounter
- Inter-Arrival Time (IAT)

Purpose:

Measure timing consistency and sequential behaviour.

---

## Statistical Features

Derived from multiple packets rather than extracted directly from a single frame.

Examples include:

- Mean IAT
- IAT Standard Deviation
- Frame Rate
- FrameID Frequency
- CycleCounter Delta Distribution

These statistical features provide the numerical representation required by machine learning algorithms.

---

# Research Insight

One of the most important observations made during today's study is that machine learning algorithms do not understand industrial protocols directly.

Instead, protocol fields are transformed into numerical features.

Example:

```text
PROFINET Frame
        ↓
Feature Extraction
        ↓
CycleCounter Delta
Inter-Arrival Time
Frame Rate
FrameID Frequency
Source MAC
Destination MAC
        ↓
Machine Learning Dataset
        ↓
Anomaly Detection Model
```

Consequently, the effectiveness of an Industrial IDS depends heavily on the quality of feature engineering rather than on the machine learning algorithm alone.

---

# Connection to Future Work

Today's work establishes the statistical baseline that will support the remaining phases of the project.

Week 4:

- Generate deterministic PROFINET RT traffic.

Week 5:

- Extract statistical protocol features.

Week 6:

- Build normal communication datasets.

Week 7–8:

- Train anomaly detection models using the generated baseline.

The baseline developed today therefore forms the foundation for all subsequent machine learning experiments.

---

# Key Takeaways

1. PROFINET RT produces deterministic cyclic communication that is well suited for anomaly detection.
2. Inter-Arrival Time (IAT) is one of the most valuable timing features in Industrial IDS.
3. Small timing variations (jitter) are normal and should be incorporated into baseline traffic generation.
4. Gaussian jitter provides a realistic simulation of industrial communication timing.
5. Industrial IDS combines identity, semantic, temporal, and statistical features to characterize normal communication.
6. Feature engineering provides the bridge between raw network packets and machine learning models.
7. A well-defined statistical baseline is essential for accurate anomaly detection in industrial control systems.





