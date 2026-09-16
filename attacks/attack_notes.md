
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
