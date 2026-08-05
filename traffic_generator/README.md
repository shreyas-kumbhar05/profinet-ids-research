# Traffic Generator — PROFINET RT Baseline

## What This Module Does

This module generates PROFINET RT cyclic traffic that behaves like
a real IO Controller communicating with field devices on an industrial
network. The output is used as the normal class baseline for training
the anomaly detection models in later stages of this project.

The key difference from a packet replay tool is that frames are
constructed programmatically with full control over timing,
CycleCounter values and protocol fields. This allows the same
generator to produce both normal industrial traffic and controlled
attack scenarios later in the project.

---



## Known Limitations

The generator maintains accurate long-term timing (mean IAT ≈ 4.001 ms
for a 4.000 ms target), but the measured inter-arrival time standard
deviation is higher than the configured Gaussian jitter when executed
inside a VirtualBox virtual machine.

This behaviour is caused by occasional operating system and hypervisor
scheduling delays rather than protocol implementation errors.
CycleCounter integrity remains unaffected, with no observed frame loss,
replays or out-of-order packets.

A detailed investigation of this behaviour is documented in
`protocol_notes/cyclic_communication.md`.
