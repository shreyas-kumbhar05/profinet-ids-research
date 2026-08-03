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


---


## Day 3 — 27/07/2026

**Focus:** Designing the configuration system for the PROFINET traffic generator before implementing the generator itself.

### Research Question

How should the traffic generator be configured so that experiment parameters can be modified easily without changing the Python source code?

---

### Sources Studied

**Real Python**

https://realpython.com/python-yaml/

Sections read

- Basic YAML syntax
- Nested keys
- Comments
- Loading YAML files using `yaml.safe_load()`

**PyPI**

https://pypi.org/project/PyYAML/

Sections read

- Basic usage
- Loading configuration files

**Python Documentation**

https://docs.python.org/3/library/argparse.html

Sections read

- `ArgumentParser()`
- `add_argument()`
- `parse_args()`

---

### What I Found

Initially, I thought configuration values such as the communication cycle time, payload size and MAC addresses could simply be defined as constants inside the Python program.

While studying YAML, I realised that separating configuration from implementation makes the generator much easier to maintain. Instead of editing Python code every time I want to run a different experiment, I can modify only the configuration file.

I also learned that YAML maps naturally to Python dictionaries when loaded using `yaml.safe_load()`. The nested structure in the YAML file becomes a nested dictionary, making configuration values straightforward to access inside the program.

Finally, I studied Python's `argparse` module and found that configuration values can also be overridden from the command line without permanently modifying the configuration file. This allows temporary experiment-specific changes while keeping the default configuration unchanged.

---

### What I Initially Thought

Before reading about YAML and PyYAML, I assumed configuration files were simply another way of storing text.

I also expected that changing experiment parameters would always require editing the configuration file itself.

After learning how `argparse` works, I realised that the configuration file only provides the default settings. Individual parameters can be overridden during program execution whenever required, allowing quick experiments without repeatedly editing and restoring the configuration file.

---

### Design Decision

The traffic generator will use a dedicated `config.yaml` file containing four logical sections:

- `generator`
- `profinet`
- `timing`
- `capture`

Grouping related parameters makes the configuration easier to understand and allows new sections to be added later without changing the overall structure.

The generator will load this configuration only once when the program starts and store it as a Python dictionary. Every other function in the program will use this dictionary instead of repeatedly reading the configuration file.

Command-line arguments will be used only for temporary overrides. The original `config.yaml` file will remain unchanged, ensuring that the default experiment configuration is always preserved.

---

### Why This Matters for My Project

This project will eventually generate multiple datasets with different communication characteristics such as varying cycle times, payload sizes and capture durations.

Keeping these parameters outside the source code makes experiments easier to reproduce and reduces the chance of accidentally modifying the implementation while changing experimental settings.

Using a structured configuration file also makes the traffic generator more scalable, since additional protocol parameters and future attack scenarios can be incorporated without restructuring the program.

---

### Architecture Planned

Before starting implementation, I planned the overall structure of `generator.py` to separate different responsibilities.

The planned functions are:

- `load_config()` — load the YAML configuration into a Python dictionary.
- `build_frame()` — construct a PROFINET RT Ethernet frame.
- `compute_jitter()` — generate realistic timing variation.
- `print_stats()` — display runtime statistics.
- `run_generator()` — execute the cyclic transmission loop.
- `parse_args()` — process command-line overrides.

Separating these responsibilities should make the implementation easier to understand, test and extend during later weeks of the project.

---

### Next Step

The next step is to begin implementing `generator.py` using the planned architecture. The first objective will be loading the configuration file, constructing valid PROFINET RT frames and preparing the timing loop that will later generate the baseline traffic dataset.



---



## Day 4 — 02/08/2026

**Focus:** Writing the first implementation of the PROFINET RT traffic generator and testing it on my Kali VM.

---

### Today's Goal

The goal today was to combine everything I studied over the last few days into one working program. Instead of learning new concepts, most of the time was spent implementing them in Python and understanding how the different parts of the generator fit together.

---

### Building the Generator

I started by implementing the functions I had planned yesterday instead of writing everything inside one large loop.

The final structure looks like this:

- `load_config()` – reads values from `config.yaml`
- `build_frame()` – constructs one PROFINET RT Ethernet frame
- `compute_jitter()` – generates Gaussian timing jitter
- `print_stats()` – reports progress while the generator runs
- `run_generator()` – controls the transmission loop
- `parse_args()` – allows configuration overrides from the command line

Breaking the program into small functions made the code much easier to read than I expected. When I needed to check something, I always knew which function was responsible for that part of the program.

---

### Reusing Previous Work

While writing `build_frame()`, I realised that Week 3 saved me a lot of work.

Instead of figuring out the PROFINET RT header again, I simply reused the same frame layout I had already studied. The only field that changes continuously is the CycleCounter, while the remaining protocol fields are loaded from `config.yaml`.

That made the implementation much simpler than starting from scratch.

---

### Configuration Instead of Hardcoding

Yesterday I wondered whether using a YAML file was worth the extra effort.

After finishing today's implementation, I changed my mind.

Almost every value used by the generator now comes from `config.yaml`, including the MAC addresses, payload size, cycle time and jitter values. The Python code no longer needs to change when I want to run a different experiment.

Using `argparse` together with the configuration file also made more sense after seeing it in actual code rather than just reading the documentation.

---

### Something I Didn't Expect

The first time I tried running the generator, it immediately failed with a `FileNotFoundError`.

After checking the traceback, I realised I had executed the program from inside the `traffic_generator` directory. The configuration path inside the program is relative to the repository root, so Python looked for:

traffic_generator/traffic_generator/config.yaml

instead of:

traffic_generator/config.yaml

Running the program from the project root fixed the problem.

This was a good reminder that Python resolves relative paths from the current working directory rather than from the location of the script itself.

---

### First Test Run

After fixing the path issue, I ran the generator for 10 seconds.

**Observed output**

```text
Expected FPS : 250.0
Actual FPS   : 14.9
Frames Sent  : 150
Elapsed Time : 10.06 s
```

The program completed without crashing, but the transmission rate was much lower than expected.

At this stage I don't know whether the bottleneck comes from Scapy, my virtual machine, the timing loop, or another part of the implementation.

Instead of assuming the cause, I'll investigate it before using this generator to create the baseline dataset.

---

### What I Learned Today

Today's work made me realise that writing code and verifying code are two different stages.

From reading the implementation alone, everything looked correct. Only after running the program did I discover that the actual performance was far from what I expected.

That is probably the biggest lesson from today. A program that runs without errors is not necessarily a program that behaves correctly.

---

### Next Step

Before generating the baseline dataset, I need to understand why the generator is only producing around 15 FPS instead of 250 FPS.

The next task will be to profile the transmission loop, identify the bottleneck and verify that the measured frame rate matches the configured cycle time before capturing traffic for later experiments.


---

## Day 5 — 03/08/2026

**Focus:** Debugging the traffic generator, generating the baseline dataset, and verifying the captured PROFINET RT traffic.

### Research Question

Can the traffic generator maintain the intended 4 ms communication cycle throughout a long capture, and if not, where is the timing error being introduced?

---

### Initial Observation

Before beginning the scheduled verification work, I tested the generator with a short 10-second run to confirm that everything was working correctly.

Although the program completed without any errors, the output was unexpected.

Instead of producing approximately **250 frames per second**, the generator was only transmitting around **15 fps**. At that speed, a 10-minute capture would produce only a small fraction of the expected dataset, so I decided to stop and investigate the generator before continuing with the scheduled tasks.

---

### First Hypothesis

My first assumption was that the compensated timing logic from Day 4 might be incorrect.

Since the communication schedule depends entirely on `next_send_ns`, I initially suspected that the timing calculations were introducing unnecessary delays.

After checking the timing calculations, the compensated scheduling algorithm appeared to be working correctly, so I looked elsewhere.

---

### Measuring the Cost of Packet Transmission

To isolate the problem, I measured how long each packet transmission required.

I temporarily wrapped the transmission call with a timer using `time.perf_counter()`.

The results were surprising.

Typical transmission times were between **40 ms and 90 ms** for a single packet.

This immediately explained why the generator was only producing around **15–20 fps** despite targeting a 4 ms communication cycle.

The delay was not coming from the timing loop itself but from the packet transmission function.

---

### Investigating sendp()

The generator was originally using Scapy's `sendp()` function for every packet.

After reading through Scapy's implementation and comparing it with the program behaviour, I realised that `sendp()` performs a considerable amount of work every time it is called.

Even though this overhead is acceptable when sending a few packets, it becomes a major bottleneck when attempting to generate hundreds of Ethernet frames every second.

---

### Design Change

Instead of repeatedly calling `sendp()`, I changed the generator to create a persistent Layer-2 socket once before entering the transmission loop.

Frames are now transmitted directly through this socket for the remainder of the capture.

The socket is closed in a `finally` block after the generator exits.

This removes the repeated setup cost while keeping the program structure almost identical.

---

### Result

After switching to a persistent Layer-2 socket, the improvement was immediate.

A 10-second test now produced approximately **250 frames per second**, matching the expected communication rate.

This confirmed that the original timing algorithm from Day 4 had not been the source of the performance issue.

---

### Verifying the Generated Traffic

With the generator working correctly, I continued with the scheduled Day 5 work.

I first reviewed the `tcpdump` EtherType filtering syntax and captured only frames with EtherType **0x8892** so that the capture would contain only PROFINET RT traffic.

I then wrote `verify_capture.py` to analyse the generated PCAP file instead of relying only on Wireshark.

The verification script checked:

- Number of captured frames
- Inter-arrival time statistics
- CycleCounter behaviour
- Frame IDs
- Frame length consistency
- Replay, dropped and out-of-order frames

---

### Verification Results

The capture produced almost exactly the expected number of packets for a 10-minute run.

The average inter-arrival time was also extremely close to the intended 4 ms communication cycle.

The verification report showed:

- Mean IAT ≈ **4.001 ms**
- Approximately **150,000 frames**
- No replay frames
- No dropped CycleCounter values
- No out-of-order packets
- Valid PROFINET FrameID
- Constant frame size

All protocol-level checks passed successfully.

---

### Unexpected Result

One value immediately stood out during verification.

Although the average inter-arrival time matched the target almost perfectly, the measured standard deviation was around **3–4 ms**, significantly higher than the configured Gaussian jitter of **0.3 ms**.

Since the generator itself appeared to be functioning correctly, I suspected that another factor was affecting the recorded timestamps.

---

### Additional Investigation

Rather than immediately changing the implementation, I decided to investigate the behaviour further.

I temporarily modified the verification script to print unusually large inter-arrival times.

I also added temporary statistics showing:

- Largest recorded delays
- Number of IAT values above 10 ms
- Distribution of inter-arrival times

These debugging additions revealed that most packets were still arriving close to the intended 4 ms interval.

Only a relatively small number of packets experienced much larger delays, with occasional gaps exceeding **300 ms**.

Interestingly, these large gaps appeared at random positions throughout the capture rather than following any repeating pattern.

CycleCounter values remained perfectly sequential even during these large timestamp gaps.

This suggested that packets were not being lost or retransmitted.

---

### Alternative Timing Experiment

I also experimented with a different compensated timing approach.

Instead of adding jitter directly into the communication schedule, I applied jitter only to the calculated sleep duration.

My expectation was that separating the ideal schedule from the operating system delay might reduce the recorded timing variance.

After generating another capture, however, the measured standard deviation became slightly worse rather than better.

Since the experiment did not improve the results, I reverted the generator to the previous implementation.

---

### External Verification

At this point I wanted to determine whether the remaining timing variation was caused by my implementation or by the execution environment itself.

I looked into the behaviour of Python's `time.sleep()` on standard Linux systems together with VirtualBox scheduling behaviour.

The information I found consistently explained that general-purpose operating systems cannot guarantee deterministic wake-up times at the sub-millisecond level.

Virtualization introduces additional scheduling delays because both the host operating system and the guest operating system participate in scheduling the virtual machine.

This matched the behaviour I was observing experimentally.

---

### Final Conclusion

By the end of the investigation, I was satisfied that the traffic generator itself was functioning correctly.

The compensated timing algorithm maintained the intended communication schedule, the generator consistently achieved approximately **250 frames per second**, and all protocol-level verification checks passed successfully.

The remaining variation in recorded inter-arrival times appears to be a limitation of running Python inside a VirtualBox virtual machine rather than an implementation error in the traffic generator itself.

Instead of continuing to modify working code, I decided to keep the stable implementation and document this limitation as part of the experimental results.

---

### Next Step

The next stage is to improve the module documentation of README.md
---
