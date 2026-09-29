# PROFINET Attack Scenarios

This directory contains the three attack scripts and the PCAP captures used to build the Week 6 dataset.

## Replay attack

Script:

```text
attacks/replay.py
```

Capture:

```text
attacks/captures/replay.pcap
```

The replay script loads previously captured valid PROFINET frames and sends selected frames again after a delay. The Week 6 experiment used 100 frames and replayed them at twice the normal 4 ms cycle rate.

The main things we expected to change were the timing and the cyclic sequence behaviour. The original FrameID and source MAC were kept unchanged.

## Source-MAC spoofing attack

Script:

```text
attacks/spoof.py
```

Capture:

```text
attacks/captures/spoof.pcap
```

The spoof script creates multiple locally administered fake MAC addresses and sends PROFINET RT frames using those addresses. Each fake MAC keeps its own sequential CycleCounter.

The main feature used to represent this attack is `src_mac_known`. The baseline MAC set comes from normal traffic, so the generated fake MACs are marked as unknown in the dataset.

## Malformed FrameID attack

Script:

```text
attacks/malformed.py
```

Capture:

```text
attacks/captures/malformed.pcap
```

The malformed attack keeps the normal source MAC and cyclic behaviour but replaces the normal PROFINET FrameID with invalid values.

The invalid values used were:

```text
0x0001
0xFFFF
0x7000
0xC500
0x0800
```

The CycleCounter remained sequential and the other header fields were kept unchanged.

## Captures

The final Week 6 capture files are:

```text
attacks/captures/replay.pcap
attacks/captures/spoof.pcap
attacks/captures/malformed.pcap
```

The PCAP packet counts used for the final dataset were:

```text
replay    → 100 packets
spoof     → 41509 packets
malformed → 41326 packets
```

The dataset has one fewer feature row than the packet count for each capture because IAT is calculated with `np.diff()`, so N packets produce N-1 IAT values.

## Ground truth

The dataset labels are assigned according to the experiment that produced each PCAP:

```text
normal.pcap    → 0 → normal
replay.pcap    → 1 → replay
spoof.pcap     → 2 → spoof
malformed.pcap → 3 → malformed
```

The labels are added by `dataset/build_dataset.py` after feature extraction.

## Current limitation

The malformed attack changes FrameID, but FrameID is not currently included in the four-feature per-frame dataset. The attack is still kept as a separate labeled class so the captured scenario is represented correctly, but a later version can add an explicit FrameID-based feature if needed.
