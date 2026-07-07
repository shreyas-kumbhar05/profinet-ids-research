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
