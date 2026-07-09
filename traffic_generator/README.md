# Traffic Generator

## Module Purpose

The Traffic Generator module is responsible for producing deterministic PROFINET RT communication that closely resembles the cyclic behaviour of industrial automation systems. The generated traffic serves as the baseline dataset for feature extraction, anomaly injection, and machine learning experiments developed in the later stages of this project.

Unlike packet replay tools, this module constructs protocol-compliant frames programmatically while controlling communication timing, packet frequency, and protocol metadata.

---

# Background Study

## Motivation

The primary objective of the traffic generator is not simply to transmit valid PROFINET RT frames, but to reproduce the temporal behaviour of an industrial control network with sufficient fidelity for machine learning experiments.

Unlike conventional software applications, where occasional timing inaccuracies are often acceptable, Industrial Ethernet protocols rely on deterministic communication. Consequently, the timing characteristics of generated traffic become part of the experimental methodology rather than merely an implementation detail.

For this reason, the timing mechanism used by the generator was investigated before any implementation work began.

---

## Python Timing Mechanisms Evaluated

Two functions from Python's `time` module were studied because they directly influence the temporal behaviour of the generated traffic.

### `time.sleep()`

`time.sleep()` suspends program execution for at least the requested duration. The operating system scheduler determines the exact wake-up time, meaning the actual delay may be slightly longer than requested depending on system load and scheduling latency.

Although suitable for introducing delays, `time.sleep()` alone cannot guarantee deterministic communication intervals.

### `time.perf_counter_ns()`

`time.perf_counter_ns()` provides a monotonic, high-resolution timer with nanosecond precision. Unlike wall-clock time, this timer is specifically intended for measuring elapsed execution time and is unaffected by system clock adjustments.

Its primary role in this project is to measure the actual execution time of each communication cycle so that timing errors can be compensated rather than accumulated.

---

## Timing Drift

An important observation made during the design study is that communication loops contain two distinct components:

- Frame generation and processing time.
- Intentional waiting time.

A naïve implementation that repeatedly performs:

```python
send_frame()
time.sleep(target_cycle)
```

does not produce the desired cycle period because the frame construction time is added to the requested sleep duration.

For example:

| Operation | Time |
|-----------|------|
| Frame construction | 0.6 ms |
| Requested sleep | 4.0 ms |
| Actual communication cycle | 4.6 ms |

The resulting frame rate becomes approximately 217 frames per second rather than the intended 250 frames per second.

Although the error appears small for a single communication cycle, it accumulates continuously throughout long-duration experiments.

---

## Importance of Long-Term Timing Accuracy

The traffic generator is expected to produce baseline datasets consisting of hundreds of thousands of frames.

A timing error of only a few hundred microseconds per communication cycle accumulates over time, causing the generated traffic to deviate from the intended statistical baseline.

Such drift changes the observed distribution of inter-arrival times and may bias later stages of feature extraction and machine learning training.

Maintaining long-term timing accuracy is therefore necessary not only for protocol realism but also for preserving the validity of the experimental dataset.

---

##  Design Decision

The following implementation will be based on a compensated scheduling algorithm that maintains communication relative to an ideal timeline instead of repeatedly delaying for a fixed duration.

Based on the observations above, the traffic generator will not rely on repeated fixed-duration sleep intervals.

Instead, future implementation will schedule each transmission relative to an ideal communication timeline measured using `time.perf_counter_ns()`. This compensated scheduling approach prevents cumulative timing drift and more closely approximates deterministic industrial communication.
