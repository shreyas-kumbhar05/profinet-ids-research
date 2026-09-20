
# Attack Notes — PROFINET IDS

## ICS-CERT Advisory Review

### Advisory 1 — Siemens SIMATIC S7-1500 CPU Firmware Vulnerabilities (ICSA-14-073-01)

- Affected system: Siemens SIMATIC S7-1500 CPU family, older firmware versions
- Vulnerability class: Includes specially crafted network packets causing denial of service
- Attack precondition: Attacker requires access to the local Ethernet segment
- Real-world impact: Specially crafted PROFINET packets could cause the device to enter defect mode and require a cold restart for recovery.

### Advisory 2 — Siemens Industrial Products (ICSA-18-023-02)

- Affected system: Siemens industrial products using PROFINET DCP
- Vulnerability class: Improper input validation
- Attack precondition: Requires network access to the local Ethernet segment
- Real-world impact: Successful exploitation could cause the targeted device to enter a denial-of-service state.

### Advisory 3 — Siemens PROFINET Stack Integrated on Interniche Stack (ICSA-22-104-06)

- Affected system: Includes multiple Siemens devices using the affected PROFINET stack
- Vulnerability class: Uncontrolled resource consumption
- Attack precondition: According to the advisory, remotely exploitable with low attack complexity 
- Real-world impact: Successful exploitation could cause a denial-of-service condition.

## Threat Model Summary

A replay attack in an industrial network involves recording previously valid
PROFINET traffic and transmitting those frames again.

The important difference from a general IT replay scenario is that PROFINET
traffic is part of a cyclic industrial control process. A packet can therefore
be correctly formatted and previously valid, but still become anomalous or invalid if it
appears at the wrong point in the communication sequence or at an unexpected
time.

For this project, the relevant indicators are the CycleCounter, inter-arrival
time and repeated frame behaviour.

The attacker is assumed to have network-level access to the PROFINET traffic
path but does not necessarily have legitimate application-level access to the
controller or device.

## Why I chose these 3 attacks

- Replay: tests whether the IDS can detect previously valid traffic being
  reused in an abnormal sequence or timing context. This connects directly
  to CycleCounter and the IAT baseline studied in Weeks 3–5.

- Spoofing: tests whether the IDS can identify frames originating from an
  unexpected source MAC address. This connects directly to the
  `src_mac_known` feature developed in Week 5.

- Malformed: tests whether the IDS can detect deviations in PROFINET frame
  structure or payload characteristics. This connects to FrameID validity,
  frame size and payload entropy studied earlier.

The three scenarios therefore provide different forms of deviation from the
normal PROFINET baseline instead of generating arbitrary abnormal traffic.


## Pseudocode — Attack 1: Replay

1. Load the 100 normal frames I already captured (Week 4/5 pcap)
2. Wait 10 seconds doing nothing
3. For each of those 100 frames, send it again unmodified
4. Send them twice as fast as they were originally sent
   (half the original gap between each send)
5. What makes this "replay" and not just "resending": CycleCounter
   values will NOT increment — they'll repeat exactly what was
   already seen, which is the anomaly signal from Week 3/5

## Pseudocode — Attack 2: Frame Spoofing

1. Decide how many fake devices to simulate (e.g. 5)
2. Generate that many random MAC addresses
3. Loop: for each frame sent, pick one of those random MACs as
   the source MAC instead of the real fixed IO Controller MAC
4. Keep everything else about the frame normal (valid FrameID,
   sequential CycleCounter per fake device)
5. What makes this "spoofing": src_mac_known feature (Week 5)
   will flip to False repeatedly — new MACs never seen in baseline

## Pseudocode — Attack 3: Malformed Function Codes

1. Build a normal frame using the same structure as profinet_frame.py
2. Instead of FrameID = 0x8001 (valid), use a FrameID OUTSIDE
   the valid range 0x8000-0xBFFF
3. Pick a few different invalid values to vary the malformation
   (e.g. 0x0001, 0xFFFF, 0x7000)
4. Send these at normal cyclic timing so ONLY the FrameID is wrong
5. What makes this detectable: frame_id_valid check (Week 3/5)
   will fail — this is a pure header integrity violation



### Implementation gap

## Implementation Gap

I understand the three attack concepts and their expected behaviour,
but I struggle to translate the design into Python when starting from
a blank file.

The main difficulty is deciding the program structure, function
breakdown, variables, control flow and the order in which the code
should be written.

This is something I need to practice during the implementation stage.
