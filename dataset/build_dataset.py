import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from feature_extractor.extractor import (
    extract_features,
    filter_profinet,
    load_pcap,
)


def get_known_macs(normal_pcap):
    packets = load_pcap(normal_pcap)
    profinet = filter_profinet(packets)

    known_macs = {
        packet["Ether"].src
        for packet in profinet
        if packet.haslayer("Ether")
    }

    if not known_macs:
        raise ValueError(
            "No source MAC addresses were found in normal PROFINET traffic."
        )

    print(f"Known MAC addresses from normal traffic: {sorted(known_macs)}")
    return known_macs


def process_capture(
    pcap_path,
    label,
    attack_type,
    known_macs,
    temp_dir,
):
    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_csv = temp_dir / f"{attack_type}_features.csv"
    temp_db = temp_dir / f"{attack_type}_features.db"

    df = extract_features(
        pcap_path,
        str(temp_csv),
        str(temp_db),
        known_macs,
    )

    if df is None:
        raise RuntimeError(
            f"Feature extraction failed for {pcap_path}"
        )

    df = df.copy()
    df["label"] = label
    df["attack_type"] = attack_type

    return df


def build_dataset(
    normal_pcap,
    replay_pcap,
    spoof_pcap,
    malformed_pcap,
    temp_dir,
):
    known_macs = get_known_macs(normal_pcap)

    scenarios = [
        (normal_pcap, 0, "normal"),
        (replay_pcap, 1, "replay"),
        (spoof_pcap, 2, "spoof"),
        (malformed_pcap, 3, "malformed"),
    ]

    dataframes = []

    for pcap_path, label, attack_type in scenarios:
        print(f"\nProcessing {attack_type} capture...")

        df = process_capture(
            pcap_path,
            label,
            attack_type,
            known_macs,
            temp_dir,
        )

        print(
            f"  {attack_type}: "
            f"{len(df)} feature rows"
        )

        dataframes.append(df)

    dataset = pd.concat(
        dataframes,
        ignore_index=True,
    )

    return dataset, known_macs


def save_dataset(df, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"\nDataset saved to: {output_path}")
    print(f"Total rows: {len(df)}")


def print_dataset_stats(df):
    print("\nDataset statistics")
    print("=" * 60)

    print(f"Total rows: {len(df)}")

    counts = df["attack_type"].value_counts()
    percentages = (
        df["attack_type"]
        .value_counts(normalize=True)
        .mul(100)
    )

    print("\nClass distribution:")

    for attack_type in ["normal", "replay", "spoof", "malformed"]:
        count = int(counts.get(attack_type, 0))
        percentage = float(percentages.get(attack_type, 0.0))

        print(
            f"  {attack_type:10s}: "
            f"{count:8d} rows "
            f"({percentage:.2f}%)"
        )

    print("\nFeature summary:")
    print(
        df[
            [
                "iat",
                "frame_size",
                "src_mac_known",
                "payload_entropy",
            ]
        ].describe()
    )


def write_dataset_stats(df, output_path, known_macs):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    counts = df["attack_type"].value_counts()
    percentages = (
        df["attack_type"]
        .value_counts(normalize=True)
        .mul(100)
    )

    stats_df = df[
        [
            "iat",
            "frame_size",
            "src_mac_known",
            "payload_entropy",
        ]
    ].copy()

    stats_df["src_mac_known"] = stats_df["src_mac_known"].astype(int)

    feature_stats = stats_df.describe()

    lines = [
        "# Dataset Statistics",
        "",
        "## Dataset overview",
        "",
        f"- Total feature rows: {len(df)}",
        f"- Number of features: 4",
        "- Ground-truth columns: `label`, `attack_type`",
        f"- Known MAC addresses from normal traffic: {len(known_macs)}",
        "",
        "## Class distribution",
        "",
        "| Label | Attack type | Rows | Percentage |",
        "|---:|---|---:|---:|",
    ]

    label_map = {
        "normal": 0,
        "replay": 1,
        "spoof": 2,
        "malformed": 3,
    }

    for attack_type in [
        "normal",
        "replay",
        "spoof",
        "malformed",
    ]:
        count = int(counts.get(attack_type, 0))
        percentage = float(percentages.get(attack_type, 0.0))

        lines.append(
            f"| {label_map[attack_type]} | "
            f"{attack_type} | "
            f"{count} | "
            f"{percentage:.2f}% |"
        )

    lines.extend(
        [
            "",
            "## Feature statistics",
            "",
            "| Statistic | IAT | Frame size | Source MAC known | Payload entropy |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for statistic in [
        "count",
        "mean",
        "std",
        "min",
        "25%",
        "50%",
        "75%",
        "max",
    ]:
        row = [
            statistic,
            feature_stats.loc[statistic, "iat"],
            feature_stats.loc[statistic, "frame_size"],
            feature_stats.loc[statistic, "src_mac_known"],
            feature_stats.loc[statistic, "payload_entropy"],
        ]

        formatted = [
            f"{value:.6f}"
            if isinstance(value, float)
            else str(value)
            for value in row
        ]

        lines.append(
            f"| {formatted[0]} | "
            f"{formatted[1]} | "
            f"{formatted[2]} | "
            f"{formatted[3]} | "
            f"{formatted[4]} |"
        )

    lines.extend(
        [
            "",
            "## Feature definitions",
            "",
            "- `iat`: inter-arrival time between consecutive PROFINET RT frames.",
            "- `frame_size`: captured Ethernet frame length in bytes.",
            "- `src_mac_known`: whether the source MAC belongs to the legitimate baseline MAC set obtained from `normal.pcap`.",
            "- `payload_entropy`: Shannon entropy of the PROFINET IO data portion.",
            "",
            "## Label semantics",
            "",
            "- `0` = normal traffic",
            "- `1` = replay traffic",
            "- `2` = spoof traffic",
            "- `3` = malformed traffic",
            "",
            "The labels come from the known experimental scenario associated with each PCAP. They are ground-truth metadata, not values inferred by the feature extractor.",
            "",
            "## Important limitation",
            "",
            "The current per-frame feature schema does not directly include the PROFINET FrameID. The malformed attack changes FrameID, so the `malformed` label identifies the attack scenario even though FrameID itself is not currently represented as a feature.",
            "",
            "The statistics above are generated from the actual extracted dataset and should be treated as the dataset-specific results for this experiment.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Dataset statistics written to: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a labeled PROFINET attack dataset"
    )

    parser.add_argument(
        "--normal-pcap",
        required=True,
        help="Path to the normal baseline PCAP",
    )

    parser.add_argument(
        "--replay-pcap",
        default="attacks/captures/replay.pcap",
        help="Path to replay PCAP",
    )

    parser.add_argument(
        "--spoof-pcap",
        default="attacks/captures/spoof.pcap",
        help="Path to spoof PCAP",
    )

    parser.add_argument(
        "--malformed-pcap",
        default="attacks/captures/malformed.pcap",
        help="Path to malformed PCAP",
    )

    parser.add_argument(
        "--output-csv",
        default="dataset/labeled_dataset.csv",
        help="Output labeled CSV",
    )

    parser.add_argument(
        "--stats",
        default="dataset/dataset_stats.md",
        help="Output dataset statistics Markdown file",
    )

    parser.add_argument(
        "--temp-dir",
        default="dataset/.tmp",
        help="Temporary directory for intermediate extractor outputs",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    dataset, known_macs = build_dataset(
        normal_pcap=args.normal_pcap,
        replay_pcap=args.replay_pcap,
        spoof_pcap=args.spoof_pcap,
        malformed_pcap=args.malformed_pcap,
        temp_dir=args.temp_dir,
    )

    save_dataset(
        dataset,
        args.output_csv,
    )

    print_dataset_stats(dataset)

    write_dataset_stats(
        dataset,
        args.stats,
        known_macs,
    )


if __name__ == "__main__":
    main()
