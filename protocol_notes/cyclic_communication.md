## Understanding Cyclic Communication

- Unlike traditional IT networks where communication occurs only when requested, PROFINET RT uses cyclic communication in which IO Controllers and IO Devices exchange process data at fixed time intervals. The communication continues continuously throughout system operation, creating highly deterministic traffic patterns.

- This deterministic behaviour makes industrial traffic significantly more predictable than enterprise network traffic and provides an excellent baseline for statistical anomaly detection.


## Why 4 ms Was Selected

- Although PROFINET supports cycle times as low as 1 ms, this project adopts a 4 ms cycle time to balance realism and computational efficiency. 
- A 4 ms cycle produces 250 frames per second, providing sufficient temporal resolution for anomaly detection while reducing CPU load, dataset size, and timing inaccuracies introduced by software-based traffic generation. 
- This makes the generated baseline both representative of industrial communication and practical for experimentation.



## Understanding Inter-Arrival Time (IAT)

- Inter-Arrival Time (IAT) is the time difference between two consecutive frames. Instead of learning absolute timestamps, an Industrial IDS learns the timing pattern between packets. 
- Since PROFINET RT communicates cyclically, IAT remains highly predictable under normal conditions, making it one of the most valuable statistical features for anomaly detection.

## Understanding Jitter

- Real industrial communication is not perfectly periodic. Small timing variations, known as jitter, naturally occur due to operating system scheduling, switch forwarding delays, and network hardware. Therefore, the traffic generator intentionally introduces small Gaussian jitter around the target 4 ms cycle time to produce realistic baseline traffic while preserving deterministic communication behaviour.





## Feature Categories for Industrial IDS

The protocol fields studied throughout Week 3 naturally fall into different feature categories.

### Identity Features
- Source MAC
- Destination MAC

Used to verify whether communication originates from expected industrial devices.

### Semantic Features
- EtherType
- FrameID

Describe the type and purpose of communication.

### Temporal Features
- CycleCounter
- Inter-Arrival Time (IAT)

Describe communication timing and sequence consistency.

### Statistical Features
- Mean IAT
- IAT Standard Deviation
- Frame Rate
- FrameID Frequency
- CycleCounter Delta Distribution

These are calculated over multiple packets and provide the baseline learned by machine learning algorithms.





## Understanding Gaussian Jitter

- Real industrial communication is deterministic but not perfectly periodic. Small timing variations naturally occur due to operating system scheduling, hardware clocks, network switches and interface processing delays. Therefore, the traffic generator introduces Gaussian jitter around the target 4 ms cycle time to produce realistic baseline traffic.

- The generator uses `random.gauss(4.0, 0.3)`, where 4.0 ms represents the expected cycle time and 0.3 ms represents the standard deviation. This produces timing values clustered around the expected cycle while preserving realistic variation.

- Using Gaussian jitter results in a baseline that more closely resembles real industrial communication than perfectly periodic traffic. Machine learning models subsequently learn this statistical distribution and identify future timing deviations as anomalies.

- The baseline defined in this document will later serve as the reference dataset for feature extraction and anomaly detection. Planned machine learning models, including Isolation Forest and LSTM, will learn the statistical characteristics of this baseline to identify deviations during runtime





## Observed vs Expected — Week 4 Generator Results

| Metric | Expected | Observed |
|---|---|---|
| IAT mean | 4.000ms | ~4.001ms |
| IAT std dev | ~0.300ms | ~3–4ms |
| Total frames (10 min) | 150,000 | ~150,000 |
| CycleCounter anomalies | 0 | 0 |

**Assessment:** Mean timing accuracy matches the target almost exactly,
confirming that the compensated timing algorithm and protocol logic are
working correctly. The measured standard deviation is higher than the
configured 0.3ms Gaussian jitter due to sporadic large delays
(occasionally exceeding 300ms) occurring at random positions throughout
the capture. These delays are not periodic and are not associated with
CycleCounter anomalies, which remained perfectly sequential.

---

## Investigation of Elevated IAT Variance

To investigate the increased timing variance, additional debugging
instrumentation was temporarily added to the verification script.

The investigation showed that most frames were transmitted within the
expected 4ms interval, while only a relatively small number of packets
experienced isolated large delays.

An alternative compensated timing implementation was also evaluated,
where Gaussian jitter was applied only to the calculated sleep duration
instead of the communication schedule itself. This modification did not
reduce the observed variance, suggesting that the timing algorithm was
not the primary source of the large delays.

**Most likely cause:** Python's `time.sleep()` on Linux provides only a
minimum waiting guarantee rather than deterministic wake-up timing.
Actual scheduling is controlled by the operating system scheduler.
Running inside VirtualBox introduces an additional scheduling layer
between the guest and host operating systems, increasing the likelihood
of occasional scheduling delays. This behaviour is consistent with the
experimental observations and is considered an environmental limitation
rather than a defect in the generator implementation.

---

## Limitation for Paper — Discussion Section

This behaviour is documented as a limitation of the current
implementation.

Although the generator maintains accurate long-term timing
(mean IAT ≈ 4ms), userspace Python running inside a virtualized
environment cannot guarantee sub-millisecond timing determinism in the
same way as dedicated PROFINET hardware operating on real-time systems.

Future work could investigate kernel-level scheduling
(e.g. `SCHED_FIFO`), PREEMPT_RT Linux kernels, or bare-metal execution
to reduce timing variance.
