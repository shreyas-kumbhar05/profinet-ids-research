# feature_extractor/extractor.py
# Extracts ML-ready features from PROFINET RT pcap captures.
#
# Usage:
#   python3 feature_extractor/extractor.py --pcap traffic_generator/captures/sample_normal.pcap

import argparse
import math
import struct
import sqlite3
import uuid
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
from scapy.all import rdpcap, Ether


def load_pcap(pcap_path):
    """Load all packets from a pcap file into memory."""
    print(f"Loading: {pcap_path}")
    packets = rdpcap(pcap_path)
    print(f"  Loaded {len(packets)} packets")
    return packets


def filter_profinet(packets):
    """Keep only frames with EtherType 0x8892."""
    filtered = [p for p in packets if p.haslayer(Ether) and p[Ether].type == 0x8892]
    print(f"  {len(filtered)} PROFINET RT frames after filtering")
    return filtered


def extract_iat(packets):
    """
    Inter-arrival time between consecutive frames, in seconds.
    First frame has no IAT — returned array is len(packets)-1.
    """
    timestamps = np.array([float(p.time) for p in packets])
    return np.diff(timestamps)


def extract_frame_sizes(packets):
    """Total frame length in bytes for each packet."""
    return [len(p) for p in packets]


def extract_ethertype_distribution(packets):
    """
    Count of each EtherType seen. Returns dict {hex_string: count}.
    For a filtered PROFINET capture this will show one dominant type.
    """
    types = [p[Ether].type for p in packets if p.haslayer(Ether)]
    counts = Counter(types)
    return {hex(k): v for k, v in counts.items()}


def extract_mac_consistency(packets, known_macs=None):
    """
    Returns list of booleans — True if src MAC matches the
    established baseline set, False if new/unknown MAC seen.
    If known_macs is None, builds the baseline from this capture itself
    (first-seen MACs become the known set).
    """
    results = []
    seen = set() if known_macs is None else set(known_macs)
    baseline_mode = known_macs is None

    for p in packets:
        if not p.haslayer(Ether):
            results.append(False)
            continue
        src = p[Ether].src
        if baseline_mode:
            seen.add(src)   # in baseline mode, every MAC becomes "known"
            results.append(True)
        else:
            results.append(src in seen)
    return results


def shannon_entropy(data: bytes) -> float:
    """Shannon entropy of a byte sequence, in bits per byte (0-8)."""
    if len(data) == 0:
        return 0.0
    counts = Counter(data)
    probs = [c / len(data) for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs)


def extract_payload_entropy(packets):
    """
    Shannon entropy of the PROFINET IO data payload
    (bytes after the 6-byte PROFINET RT header).
    """
    entropies = []
    for p in packets:
        raw = bytes(p[Ether].payload)
        io_data = raw[6:]   # skip FrameID(2) + CycleCounter(2) + DataStatus(1) + TransferStatus(1)
        entropies.append(shannon_entropy(io_data))
    return entropies


def build_feature_dataframe(packets):
    """
    Combines all extracted features into a single DataFrame.
    Note: IAT has one fewer value than other features (no IAT for frame 0),
    so we align by dropping the first frame's other features to match.
    """
    iats            = extract_iat(packets)
    frame_sizes     = extract_frame_sizes(packets)
    mac_consistency = extract_mac_consistency(packets)
    payload_entropy = extract_payload_entropy(packets)

    # Align lengths — drop index 0 for size/mac/entropy to match IAT length
    df = pd.DataFrame({
        "iat":              iats,
        "frame_size":       frame_sizes[1:],
        "src_mac_known":    mac_consistency[1:],
        "payload_entropy":  payload_entropy[1:],
    })

    return df


def save_to_csv(df, path):
    df.to_csv(path, index=False)
    print(f"  Saved CSV: {path}  ({len(df)} rows)")


def save_to_sqlite(df, db_path, session_metadata):
    """
    Saves features to SQLite with a separate metadata table
    linked by session_id.
    """
    conn = sqlite3.connect(db_path)

    # Add session_id column to features
    df = df.copy()
    df["session_id"] = session_metadata["session_id"]

    df.to_sql("features", conn, if_exists="append", index=False)

    # Save session metadata
    meta_df = pd.DataFrame([session_metadata])
    meta_df.to_sql("sessions", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"  Saved SQLite: {db_path}")


def print_summary(df):
    """Print descriptive statistics for each feature."""
    print("\n" + "=" * 55)
    print("Feature Summary Statistics")
    print("=" * 55)
    print(df.describe())
    print()
    mac_col = "src_mac_known"
    print(f"MAC consistency — known: {df[mac_col].sum()} / {len(df)}")


def extract_features(pcap_path, output_csv, output_db):
    """Main pipeline: pcap -> filtered -> features -> CSV + SQLite."""
    packets   = load_pcap(pcap_path)
    profinet  = filter_profinet(packets)

    if len(profinet) < 2:
        print("ERROR: Not enough PROFINET frames to extract IAT features.")
        return None

    ethertype_dist = extract_ethertype_distribution(packets)
    print(f"\n  EtherType distribution: {ethertype_dist}")

    df = build_feature_dataframe(profinet)

    session_metadata = {
        "session_id":        str(uuid.uuid4())[:8],
        "capture_timestamp": datetime.now().isoformat(),
        "source_pcap":       pcap_path,
        "total_frames":      len(profinet),
    }

    save_to_csv(df, output_csv)
    save_to_sqlite(df, output_db, session_metadata)
    print_summary(df)

    return df


def parse_args():
    p = argparse.ArgumentParser(description="PROFINET feature extractor")
    p.add_argument("--pcap",   required=True, help="Path to input pcap file")
    p.add_argument("--csv",    default="feature_extractor/sample_features.csv")
    p.add_argument("--db",     default="feature_extractor/features.db")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    extract_features(args.pcap, args.csv, args.db)
