# Traffic Generator — PROFINET RT Baseline

## Purpose

This module is responsible for generating the normal PROFINET RT traffic
used throughout the rest of this project.

Rather than replaying an existing packet capture, every Ethernet frame is
built from scratch using configurable protocol fields, timing parameters
and MAC addresses. This makes it possible to control the communication
cycle and later extend the same generator to create abnormal traffic for
attack simulations.

The generated traffic is captured with `tcpdump` and stored as a PCAP
file. Starting from Week 5, this capture is used as the normal dataset
for feature extraction and machine learning experiments.

---

## Quick Start

Move to the project root before running the generator.

```bash
cd ~/profinet-ids-research
```

The generator reads its settings from
`traffic_generator/config.yaml`. The cycle time and duration can also be
changed from the command line when needed.

### Generate Traffic

```bash
# Default configuration (4 ms cycle time, 10-minute run)
sudo python3 traffic_generator/generator.py

# Run with a different cycle time
sudo python3 traffic_generator/generator.py --cycle-time 2.0

# Short test run
sudo python3 traffic_generator/generator.py --duration 30
```

### Capture Generated Traffic

```bash
# Start packet capture
sudo tcpdump -i eth0 \
-w traffic_generator/captures/sample_normal.pcap \
ether proto 0x8892 &

# Run the generator
sudo python3 traffic_generator/generator.py

# Stop packet capture
sudo pkill tcpdump
```

After the capture finishes, verify that everything looks correct before
using it elsewhere in the project.

```bash
python3 traffic_generator/verify_capture.py
```

---

## Configuration

Most generator settings are stored in
`traffic_generator/config.yaml`.

For permanent changes, edit the configuration file directly.
For quick experiments, the cycle time and duration can be changed from
the command line without modifying the YAML file.

| Parameter | Default | Description |
|------------|---------|-------------|
| `timing.cycle_time_ms` | `4.0` | Communication cycle time in milliseconds. |
| `timing.jitter_std_ms` | `0.3` | Standard deviation of the Gaussian timing jitter. |
| `timing.jitter_max_ms` | `1.0` | Maximum absolute jitter allowed for each cycle. |
| `capture.duration_seconds` | `600` | Generator runtime in seconds. |
| `capture.log_interval` | `250` | Number of transmitted frames between progress updates. |
| `profinet.frame_id` | `0x8001` | PROFINET RT FrameID used in generated traffic. |
| `profinet.payload_size` | `40` | Size of the simulated IO payload (bytes). |
| `generator.interface` | `eth0` | Network interface used for Layer-2 transmission. |
| `generator.src_mac` | Configured in YAML | Source MAC address. |
| `generator.dst_mac` | Configured in YAML | Destination MAC address (PROFINET multicast by default). |
| `generator.ethertype` | `0x8892` | EtherType used for PROFINET RT frames. |

### Command-Line Overrides

Only the following settings can be overridden without editing
`config.yaml`:

```bash
sudo python3 traffic_generator/generator.py --cycle-time 2.0
sudo python3 traffic_generator/generator.py --duration 30
```

All remaining values are loaded directly from the configuration file.

---

## Generated Frame Structure

Every transmitted packet follows the basic PROFINET RT frame layout.
Only the CycleCounter changes continuously during transmission, while
the remaining protocol fields stay constant unless they are modified in
the configuration file.

### Ethernet Header

| Field | Value |
|------|------|
| Destination MAC | `01:0e:cf:00:00:00` (PROFINET IO multicast) |
| Source MAC | Configurable (`config.yaml`) |
| EtherType | `0x8892` (PROFINET RT) |

### PROFINET RT Header

| Field | Value |
|------|------|
| FrameID | `0x8001` (RT Class 1 cyclic communication) |
| CycleCounter | Starts at `0`, increments every frame and wraps after `65535` |
| DataStatus | `0x35` |
| TransferStatus | `0x00` |

### IO Data Payload

The payload contains **40 bytes** of simulated cyclic IO data. For now,
the payload is filled with zero bytes because the goal is to generate a
stable baseline dataset before introducing anomalies in later stages of
the project.

For more details about the protocol fields, refer to:

- `protocol_notes/frame_structure.md`
- `protocol_notes/cyclic_communication.md`

---

## Expected Output

Using the default configuration (4 ms cycle time for 10 minutes), the
generator should produce results close to the following.

| Metric | Target Value |
|---------|--------------|
| Total frames | ~150,000 |
| Mean Inter-Arrival Time (IAT) | 4.000 ms |
| Configured Gaussian jitter | 0.300 ms |
| CycleCounter | Sequential (+1 every frame) |
| FrameID | `0x8001` |
| Frame length | 60 bytes |

> **Note**
>
> The configured jitter value (`0.3 ms`) represents the intended timing
> behaviour of the generator. When running inside a VirtualBox virtual
> machine, the measured IAT standard deviation is noticeably higher
> because packet timestamps are affected by operating system scheduling
> and virtualization overhead. More information is available in the
> **Known Limitations** section and
> `protocol_notes/cyclic_communication.md`.

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

---

## Verifying the Capture

Before using a capture for feature extraction, run the verification
script to confirm that the generated traffic matches the expected
PROFINET RT behaviour.

```bash
python3 traffic_generator/verify_capture.py
```

The script checks:

- Total number of captured frames
- Inter-arrival time statistics
- CycleCounter continuity
- Replay or out-of-order frames
- FrameID validity
- Frame length consistency

If any of these checks fail, the capture should be investigated before
being used as the baseline dataset.

---

## Design Decisions

### Why 4 ms?

I chose a 4 ms communication cycle because it is commonly used in
PROFINET RT systems and provides a good balance between capture time and
dataset size. A 10-minute run generates roughly 150,000 frames, which is
sufficient for the feature extraction stage without producing an
unnecessarily large PCAP.

### Why Gaussian jitter?

Real industrial communication is never perfectly periodic. Small timing
variations are expected because of operating system scheduling, network
stack latency and switching delays. A Gaussian distribution models this
behaviour more realistically than choosing timing offsets uniformly.

### Why compensated timing?

The first implementation simply called `time.sleep()` after every frame.
During testing, this caused the transmission schedule to drift because
frame construction and transmission time were included in every loop
iteration.

The final implementation schedules each transmission relative to the
original start time. This keeps the average cycle time close to the
target even during long captures.

The development process, debugging sessions and timing experiments are
documented in:

- `traffic_generator/notes.md`
- `protocol_notes/cyclic_communication.md`

---

## Requirements

The following Python packages are required:

- Python 3
- Scapy
- PyYAML
- dpkt

Install everything using:

```bash
pip install -r requirements.txt
```

---

## Output Files

| File | Description |
|------|-------------|
| `captures/sample_normal.pcap` | Baseline PROFINET RT traffic capture generated by the module. |

The generated capture is used as the normal dataset for the feature
extraction stage implemented in Week 5.

Daily development notes are available in
`traffic_generator/notes.md`, while protocol-specific explanations and
observations are stored in `protocol_notes/`.
