
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

# Development Log

## Day 1 — 14/07/2026

**Focus:** Studying Python timing functions before implementing the traffic generator.

### Research Question

How can I generate PROFINET RT traffic at a fixed 4 ms cycle time without gradually drifting away from the intended communication schedule?

---

### Source Studied

**Python Documentation**

https://docs.python.org/3/library/time.html

**Sections read**

- `time.sleep()` — behaviour, OS scheduler dependency, "at least" guarantee
- `time.perf_counter_ns()` — monotonic timer, nanosecond resolution and elapsed time measurement

---

### What I Found

While reading the Python documentation, I noticed that `time.sleep()` suspends execution for **at least** the requested duration. The exact wake-up time depends on the operating system scheduler, so the process may resume slightly later than requested.

I also looked into `time.perf_counter_ns()`. Unlike `time.time()`, it provides a high-resolution monotonic timer designed for measuring elapsed execution time, making it more suitable for timing-sensitive applications like this project.

---

### What I Initially Thought

At first I assumed repeatedly calling

```python
send_frame()
time.sleep(0.004)
```

would naturally produce a constant 4 ms communication cycle.

After working through a few timing calculations, I realised that the time required to build and process each frame is added to the requested sleep duration.

---

### What I Concluded

The communication cycle is not determined only by the sleep duration.

Instead,

```
Cycle Time

=

Frame Construction

+

Sleep Time
```

If constructing one frame takes approximately **0.6 ms**, the actual communication cycle becomes

```
0.6 + 4.0 = 4.6 ms
```

instead of the intended **4.0 ms**.

This initially looked like a very small error, but after calculating the frame rate I realised it reduces the output from approximately **250 fps** to **217 fps**.

Over a 10-minute capture this would produce around **20,000 fewer frames**, shifting the Inter-Arrival Time (IAT) distribution that the anomaly detection model will later learn.

---

### Design Decision

Instead of repeatedly sleeping for 4 ms, I will maintain an ideal communication timeline and calculate how much time remains before the next scheduled transmission.

This means the scheduler follows the planned timeline rather than the completion time of the previous frame.

One idea that confused me initially was why the schedule should not simply restart whenever a frame is delayed. After working through several examples, I realised that resetting the schedule would permanently shift every future transmission. The correct approach is to keep the original schedule fixed and only adjust the remaining sleep time.

If the generator falls behind schedule (`sleep_ns <= 0`), it should transmit the frame immediately instead of waiting again. Waiting would only increase the accumulated timing error.

---

### Why This Matters for My Project

The traffic generated in this module becomes the normal baseline dataset used throughout the rest of the project.

If the average communication cycle slowly drifts from **4.0 ms** to **4.6 ms**, the feature extractor will calculate incorrect Inter-Arrival Time statistics. The machine learning model would then learn a shifted definition of normal communication, making later anomaly detection experiments less reliable.

For that reason, I decided to understand the timing behaviour before writing any generator code.

---

### Next Step

The next step is to study how real PROFINET networks maintain cyclic communication and how normal timing jitter appears in industrial traffic. That understanding will guide the implementation of the traffic generator in the following days.

---


## Day 2 — 17/07/2026

**Focus:** Reading and understanding a research paper related to my PROFINET IDS project.

### Research Question

How  does the research paper "Detecting Anomalies in Network Traffic Using Maximum Entropy Estimation" by Yu Gu, Andrew McCallum, Don Towsley Academic paper on network baseline modeling help me understand my project better


### Paper Details -  
**Title:** Detecting Anomalies in Network Traffic Using Maximum Entropy Estimation  
**Authors:** Yu Gu, Andrew McCallum, Don Towsley
**Year:** 2005
**Source:** https://www.usenix.org/legacy/event/imc05/tech/full_papers/gu/gu.pdf


### How they define baseline
Baseline is defined as normal distribution of packet classes learnt from previously collected and cleaned network traffic. The new traffic is continously compared against the learned distribution, if difference becomes large, the traffic is considered abnormal 

### Detection of anomalous traffic

The researchers compared the current traffic distribution to the learned baseline. Large deviations could be a sudden or gradual increase in the relative entropy, and are treated as anomalies


### Dataset used

They used a prelabelled dataset and the anomalies were labelled by human, and the labelled anomalous packets are removed


### My observation
This was my first academic paper on anomaly detection. I expected it to be heavily based on terms like network protocols, packets, and IDS, but it was mainly focused on mathematical terms like probability theory and information theory.

I realised that many networking research papers rely heavily on mathematics to show the working of the detection methods, even when the implementation is relatively straightforward 


