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
