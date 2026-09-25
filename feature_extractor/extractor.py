import argparse
import math
import sqlite3
import uuid
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
from scapy.all import Ether, rdpcap


def load_pcap(pcap_path):
    print(f"Loading: {pcap_path}")
    packets = rdpcap(pcap_path)
    print(f"  Loaded {len(packets)} packets")
    return packets


def filter_profinet(packets):
    filtered = [
        p for p in packets
        if p.haslayer(Ether) and p[Ether].type == 0x8892
    ]
    print(f"  {len(filtered)} PROFINET RT frames after filtering")
    return filtered


def extract_iat(packets):
    timestamps = np.array([float(p.time) for p in packets])
    return np.diff(timestamps)


def extract_frame_sizes(packets):
    return [len(p) for p in packets]


def extract_ethertype_distribution(packets):
    types = [p[Ether].type for p in packets if p.haslayer(Ether)]
    counts = Counter(types)
    return {hex(k): v for k, v in counts.items()}


def extract_mac_consistency(packets, known_macs=None):
    results = []
    seen = set() if known_macs is None else set(known_macs)
    baseline_mode = known_macs is None

    for p in packets:
        if not p.haslayer(Ether):
            results.append(False)
            continue

        src = p[Ether].src

        if baseline_mode:
            seen.add(src)
            results.append(True)
        else:
            results.append(src in seen)

    return results


def shannon_entropy(data: bytes) -> float:
    if len(data) == 0:
        return 0.0

    counts = Counter(data)
    probs = [c / len(data) for c in counts.values()]

    return -sum(p * math.log2(p) for p in probs)


def extract_payload_entropy(packets):
    entropies = []

    for p in packets:
        raw = bytes(p[Ether].payload)
        io_data = raw[6:]
        entropies.append(shannon_entropy(io_data))

    return entropies


def build_feature_dataframe(packets, known_macs=None):
    iats = extract_iat(packets)
    frame_sizes = extract_frame_sizes(packets)
    mac_consistency = extract_mac_consistency(packets, known_macs)
    payload_entropy = extract_payload_entropy(packets)

    df = pd.DataFrame({
        "iat": iats,
        "frame_size": frame_sizes[1:],
        "src_mac_known": mac_consistency[1:],
        "payload_entropy": payload_entropy[1:],
    })

    return df


def save_to_csv(df, path):
    df.to_csv(path, index=False)


def save_to_sqlite(df, db_path, session_metadata):
    conn = sqlite3.connect(db_path)

    df = df.copy()
    df["session_id"] = session_metadata["session_id"]

    df.to_sql(
        "features",
        conn,
        if_exists="append",
        index=False
    )

    meta_df = pd.DataFrame([session_metadata])

    meta_df.to_sql(
        "sessions",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()
    conn.close()


def print_summary(df):
    print(df.describe())

    mac_col = "src_mac_known"
    print(
        f"MAC consistency — known: "
        f"{df[mac_col].sum()} / {len(df)}"
    )


def extract_features(
    pcap_path,
    output_csv,
    output_db,
    known_macs=None
):
    packets = load_pcap(pcap_path)

    profinet = filter_profinet(packets)

    if len(profinet) < 2:
        print(
            "ERROR: Not enough PROFINET frames "
            "to extract IAT features."
        )
        return None

    ethertype_dist = extract_ethertype_distribution(packets)
    print(f"  EtherType distribution: {ethertype_dist}")

    df = build_feature_dataframe(
        profinet,
        known_macs
    )

    session_metadata = {
        "session_id": str(uuid.uuid4())[:8],
        "capture_timestamp": datetime.now().isoformat(),
        "source_pcap": pcap_path,
        "total_frames": len(profinet),
    }

    save_to_csv(df, output_csv)
    save_to_sqlite(df, output_db, session_metadata)

    print_summary(df)

    return df


def parse_args():
    p = argparse.ArgumentParser(
        description="PROFINET feature extractor"
    )

    p.add_argument(
        "--pcap",
        required=True
    )

    p.add_argument(
        "--csv",
        default="feature_extractor/sample_features.csv"
    )

    p.add_argument(
        "--db",
        default="feature_extractor/features.db"
    )

    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    extract_features(
        args.pcap,
        args.csv,
        args.db
    )
