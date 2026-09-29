# Dataset

This module converts the recorded PROFINET traffic PCAPs into one labeled dataset for later analysis and ML experiments.

## Input captures

The dataset is built from four traffic scenarios:

- normal baseline traffic
- replay attack
- spoof attack
- malformed FrameID attack

The three attack captures are stored in `attacks/captures/`.

## Features

The current dataset contains four per-frame features:

| Column | Description |
|---|---|
| `iat` | Time between consecutive PROFINET RT frames |
| `frame_size` | Ethernet frame length in bytes |
| `src_mac_known` | Whether the source MAC belongs to the normal baseline MAC set |
| `payload_entropy` | Shannon entropy of the PROFINET IO data portion |

The dataset also contains two ground-truth columns:

| Column | Description |
|---|---|
| `label` | Numeric class label |
| `attack_type` | Name of the traffic scenario |

## Labels

```text
0 → normal
1 → replay
2 → spoof
3 → malformed
```

## MAC baseline

The legitimate source MAC set is obtained only from `normal.pcap`.

The same `known_macs` set is passed to the extractor for normal, replay, spoof and malformed traffic. This is required so that a fake MAC introduced by the spoof attack is treated as unknown instead of becoming part of the baseline.

## Building the dataset

From the project root:

```bash
python3 dataset/build_dataset.py \
    --normal-pcap traffic_generator/captures/sample_normal.pcap
```

The attack capture paths have defaults in `build_dataset.py`:

```text
attacks/captures/replay.pcap
attacks/captures/spoof.pcap
attacks/captures/malformed.pcap
```

Optional paths can be passed through the command line when needed.

## Output

The script creates:

```text
dataset/labeled_dataset.csv
dataset/dataset_stats.md
```

Temporary extractor outputs are written to `dataset/.tmp/` during the run and should not be committed.

## Dataset result

The current generated dataset contains 232900 feature rows.

The class distribution is:

```text
normal       149968
replay           99
spoof         41508
malformed     41325
```

The replay class is much smaller because only 100 replay frames were captured.

## Current limitations

The current feature extractor does not include PROFINET FrameID as a per-frame feature, even though FrameID is the field changed by the malformed attack.

Frame size stays at 60 bytes in the current dataset and payload entropy stays at zero because of the way the traffic was generated.

These points should be considered before using the dataset for later ML experiments.
