# Dataset Statistics

## Dataset overview

- Total feature rows: 232900
- Number of features: 4
- Ground-truth columns: `label`, `attack_type`
- Known MAC addresses from normal traffic: 1

## Class distribution

| Label | Attack type | Rows | Percentage |
|---:|---|---:|---:|
| 0 | normal | 149968 | 64.39% |
| 1 | replay | 99 | 0.04% |
| 2 | spoof | 41508 | 17.82% |
| 3 | malformed | 41325 | 17.74% |

## Feature statistics

| Statistic | IAT | Frame size | Source MAC known | Payload entropy |
|---|---:|---:|---:|---:|
| count | 232900.000000 | 232900.000000 | 232900.000000 | 232900.000000 |
| mean | 0.005151 | 60.000000 | 0.821778 | 0.000000 |
| std | 0.004392 | 0.000000 | 0.382701 | 0.000000 |
| min | 0.000116 | 60.000000 | 0.000000 | -0.000000 |
| 25% | 0.003331 | 60.000000 | 1.000000 | -0.000000 |
| 50% | 0.004817 | 60.000000 | 1.000000 | -0.000000 |
| 75% | 0.006275 | 60.000000 | 1.000000 | 0.000000 |
| max | 0.558439 | 60.000000 | 1.000000 | -0.000000 |

## Feature definitions

- `iat`: inter-arrival time between consecutive PROFINET RT frames.
- `frame_size`: captured Ethernet frame length in bytes.
- `src_mac_known`: whether the source MAC belongs to the legitimate baseline MAC set obtained from `normal.pcap`.
- `payload_entropy`: Shannon entropy of the PROFINET IO data portion.

## Label semantics

- `0` = normal traffic
- `1` = replay traffic
- `2` = spoof traffic
- `3` = malformed traffic

The labels come from the known experimental scenario associated with each PCAP. They are ground-truth metadata, not values inferred by the feature extractor.

## Important limitation

The current per-frame feature schema does not directly include the PROFINET FrameID. The malformed attack changes FrameID, so the `malformed` label identifies the attack scenario even though FrameID itself is not currently represented as a feature.

The statistics above are generated from the actual extracted dataset and should be treated as the dataset-specific results for this experiment.
