# Protocol Notes — Sources and References

## Why This File Exists

This document records every primary and secondary source consulted during the protocol study conducted in Week 3 of this research project. Maintaining a transparent record of all references improves the reproducibility of the methodology and allows future readers to verify how protocol knowledge, implementation decisions, and security assumptions were derived.

Rather than relying on a single reference, protocol behaviour was verified by combining official documentation (where accessible), open-source protocol dissectors, and publicly available industrial security advisories.

---

# Primary Sources

## 1. Wireshark PROFINET RT Dissector

**Repository**

https://github.com/wireshark/wireshark

**File**

```
plugins/epan/profinet/packet-pn-rt.c
```

**Local Version Used**

- Wireshark 4.6.3
- Kali Linux
- Verified using:

```bash
wireshark --version
```

**Purpose**

The dissector source code was studied to understand how Wireshark identifies and parses PROFINET RT packets. It was primarily used to verify:

- EtherType identification
- Frame structure
- FrameID extraction
- CycleCounter extraction
- DataStatus field
- TransferStatus field
- Packet decoding workflow

**Why This Source Was Used**

The official PROFINET specification was unavailable for download during the study. The Wireshark dissector provides an independently implemented protocol parser that has been validated against real industrial deployments and is widely trusted by protocol analysts.

---

## 2. PROFINET Specification Information

**Source**

https://www.profibus.com/profinet-specification

https://www.profibus.com/download

**Status During This Study**

The official PROFINET IO Base Specification could not be obtained.

Although the PROFIBUS & PROFINET International (PI) website provides publicly accessible specification pages, the detailed protocol documents required for implementation remain restricted behind member registration and licensing requirements.

Consequently, protocol implementation details were verified using:

- Wireshark dissector source code
- Public PI documentation
- Public Siemens technical documentation
- Experimental validation using manually constructed PROFINET RT frames

**Sections Referenced Conceptually**

- PROFINET Architecture
- Frame Structure
- Real-Time Communication
- Cyclic Communication

---

# Secondary Sources

## 3. CISA Industrial Control System Advisories

**Source**

https://www.cisa.gov/ics-advisories

**Purpose**

Two Industrial Control System (ICS) advisories were reviewed to understand real-world attack scenarios affecting industrial automation systems.

The advisories were used to study:

- Industrial attack surfaces
- Engineering workstation compromise
- Device vulnerabilities
- Possible impacts on industrial communication
- Security considerations relevant to Industrial IDS design

The advisories were not used to study protocol implementation details but to establish the threat model used throughout this project.

---

## 4. Siemens Public PROFINET Documentation

**Source**

https://www.siemens.com/profinet

Additional publicly available Siemens technical articles and documentation were consulted where required.

**Purpose**

Used to understand:

- PROFINET architecture
- Industrial communication concepts
- IO Controller
- IO Device
- Engineering workflows

---

# Experimental Sources

In addition to written references, protocol understanding was validated experimentally through self-developed implementations.

The following artefacts were produced during Week 3:

- Manual construction of a minimal PROFINET RT frame using Scapy
- Validation of Ethernet and PROFINET RT header fields
- Byte-by-byte frame annotation
- Manual decoding of hexadecimal frame contents
- Verification of FrameID, CycleCounter, DataStatus and TransferStatus values
- Development of a statistical timing baseline for cyclic communication

These experiments served as practical verification of the concepts studied from the written sources.

---

# Limitation Statement

The official PROFINET IO Base Specification was not accessible during the initial phase of this project because the required implementation documents are distributed through PROFIBUS & PROFINET International (PI) under restricted access.

To minimise dependence on undocumented assumptions, protocol field definitions and parsing behaviour were cross-verified using the Wireshark PROFINET RT dissector, publicly available vendor documentation, and practical experimentation performed within this project.

Future revisions of this repository will incorporate direct references to the official specification if access becomes available.

---

# Source Reliability

| Source | Reliability | Purpose |
|----------|------------|----------|
| Wireshark PROFINET RT Dissector | High | Protocol parsing and field verification |
| PROFIBUS & PROFINET International | High | Official protocol documentation |
| Siemens Documentation | High | Industrial deployment concepts |
| CISA ICS Advisories | High | Industrial threat modelling |
| Practical Experiments | High | Independent verification of implementation |

---

# Reproducibility

A reader wishing to reproduce the protocol study performed during Week 3 should:

1. Install Wireshark 4.6.3 or a compatible version.
2. Clone the Wireshark repository and review the PROFINET RT dissector.
3. Review the publicly available PROFINET documentation published by PROFIBUS & PROFINET International.
4. Review the referenced CISA ICS advisories to understand the threat model.
5. Execute `week3/profinet_frame.py` to generate and inspect a minimal valid PROFINET RT frame.
6. Compare the generated frame against `week3/frame_annotation.md` to verify every byte of the constructed packet.

This combination of literature review, source-code analysis, and experimental validation forms the methodology adopted throughout Week 3.
