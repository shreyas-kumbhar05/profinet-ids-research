# Traffic Generator — PROFINET RT Baseline

## What This Module Does

This module generates PROFINET RT cyclic traffic that behaves like
a real IO Controller communicating with field devices on an industrial
network. The output is used as the normal class baseline for training
the anomaly detection models in later stages of this project.

The key difference from a packet replay tool is that frames are
constructed programmatically with full control over timing, cycle
counter values, and protocol fields — so the traffic can be made
to look normal, or deliberately broken, depending on what the
experiment needs.

---

## Study Notes — Before Writing Any Code

I studied the timing problem before touching the implementation
because getting the cycle time wrong would corrupt the training
dataset — and a corrupted baseline means the ML model learns
the wrong definition of "normal".

---

### Python Timing — What I Studied

**Source:** docs.python.org/3/library/time.html
**Focus:** `time.sleep()` and `time.perf_counter_ns()`

---

#### time.sleep()

Suspends execution for at least the requested duration.
The OS scheduler decides when to actually wake the process,
so the real delay is always slightly longer than requested.

The key word is "at least" — sleep(0.004) might actually
sleep for 0.0042 or 0.0043 seconds depending on what else
the system is doing. Fine for most things, but a problem
when you need 250 frames per second consistently.

---

#### time.perf_counter_ns()

High-resolution monotonic timer, returns nanoseconds as an integer.
Not affected by system clock changes. Specifically designed for
measuring elapsed time in performance-sensitive code.

I'll use this to measure how long each cycle actually took,
then compensate the next sleep to stay on the ideal timeline.

---

#### The Drift Problem

This is what made the timing study necessary before coding.

A naive loop looks like this:

```python
while True:
    send_frame()
    time.sleep(0.004)   # 4ms
```

The problem is that `send_frame()` itself takes time.
If frame construction takes 0.6ms, the actual cycle is:

```
0.6ms (construction) + 4.0ms (sleep) = 4.6ms per cycle
```

That gives ~217 fps instead of the intended 250 fps.

Over a 10-minute capture that means:

```
Expected: 250 × 600 = 150,000 frames
Actual:   217 × 600 = 130,200 frames
```

About 20,000 missing frames — and the IAT distribution
shifts from 4.0ms mean to 4.6ms mean. The feature extractor
in Week 5 would then learn the wrong baseline statistics.

---

#### The Fix — Compensated Timing

Instead of sleeping for a fixed duration each cycle,
the generator will calculate the next ideal send time
relative to the start, and sleep only for whatever
remains:

```python
cycle_ns     = 4_000_000        # 4ms in nanoseconds
next_send_ns = time.perf_counter_ns()

while True:
    send_frame()
    next_send_ns += cycle_ns    # advance ideal timeline by 4ms
    sleep_ns = next_send_ns - time.perf_counter_ns()
    if sleep_ns > 0:
        time.sleep(sleep_ns / 1_000_000_000)
```

The key insight: `next_send_ns` advances by exactly 4ms each
iteration regardless of how long the frame took to build.
The sleep compensates for whatever time was spent on construction.
Drift doesn't accumulate because each cycle is anchored to
the start, not to the previous frame.

I'll add Gaussian jitter on top of this to simulate real
network timing variance — but the compensated base keeps
the long-term mean accurate even with jitter applied.

---

#### Why This Matters for the Dataset

The training dataset will have ~150,000 frames.
A timing error of a few hundred microseconds per cycle
accumulates into a measurable shift in the IAT distribution.

If the baseline IAT mean is 4.6ms instead of 4.0ms, then:
- The feature extractor learns a shifted normal distribution
- The anomaly detector uses the wrong threshold
- Attack traffic timed at 4.0ms might appear anomalous

Getting the timing right here prevents a systematic bias
that would be very difficult to debug later in training.

---

[Day 2 content will be added here]

---

## Quick Start

```bash
# Default — 4ms cycle time, 10 minutes
sudo python3 traffic_generator/generator.py

# Short test run
sudo python3 traffic_generator/generator.py --duration 30

# Custom cycle time
sudo python3 traffic_generator/generator.py --cycle-time 2.0
```

## Configuration

All parameters are in `config.yaml`. Key ones:

| Parameter | Default | What it Controls |
|---|---|---|
| `timing.cycle_time_ms` | 4.0 | Target cycle time |
| `timing.jitter_std_ms` | 0.3 | Gaussian jitter std dev |
| `capture.duration_seconds` | 600 | Run duration |
| `profinet.frame_id` | 0x8001 | RT FrameID |
| `profinet.payload_size` | 40 | IO data bytes |

## Requirements

```
scapy
pyyaml
```
