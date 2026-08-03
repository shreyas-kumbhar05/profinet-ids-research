# traffic_generator/verify_capture.py
# Reads generated PROFINET pcap and verifies output matches spec.
#
# Run:
#     python3 traffic_generator/verify_capture.py
#
# Source reference:
# Extends week1/pcap_reader.py logic.

import dpkt
import struct
import statistics


def verify(pcap_path="traffic_generator/captures/sample_normal.pcap"):
    print(f"Reading: {pcap_path}\n")

    timestamps = []
    cycle_counters = []
    frame_lengths = []
    frame_ids = []
    errors = 0

    with open(pcap_path, "rb") as f:
        pcap = dpkt.pcap.Reader(f)

        for ts, buf in pcap:
            try:
                eth = dpkt.ethernet.Ethernet(buf)

                if eth.type != 0x8892:
                    errors += 1
                    continue

                payload = bytes(eth.data)

                frame_id = struct.unpack(">H", payload[0:2])[0]
                cycle_counter = struct.unpack(">H", payload[2:4])[0]

                timestamps.append(ts)
                cycle_counters.append(cycle_counter)
                frame_lengths.append(len(buf))
                frame_ids.append(frame_id)

            except Exception:
                errors += 1

    if not timestamps:
        print("ERROR: No PROFINET frames found.")
        print("Check that EtherType filter was applied during capture.")
        return

    iats_ms = [
        (timestamps[i] - timestamps[i - 1]) * 1000
        for i in range(1, len(timestamps))
    ]

    cc_deltas = [
        cycle_counters[i] - cycle_counters[i - 1]
        for i in range(1, len(cycle_counters))
    ]

    cc_deltas = [d if d >= 0 else d + 65536 for d in cc_deltas]

    print("=" * 58)
    print("Capture Verification Report")
    print("=" * 58)

    print("\nFrame Count")
    print(f"  Captured        : {len(timestamps)}")
    print(f"  Expected (~10m) : {250 * 600}")
    print(f"  Parse errors    : {errors}")

    print("\nInter-Arrival Time")
    print(f"  Mean            : {statistics.mean(iats_ms):.3f}ms  (target: 4.000ms)")
    print(f"  Std dev         : {statistics.stdev(iats_ms):.3f}ms  (target: ~0.300ms)")
    print(f"  Min             : {min(iats_ms):.3f}ms")
    print(f"  Max             : {max(iats_ms):.3f}ms")

    print("\nCycleCounter")
    print(f"  Normal (delta=1): {cc_deltas.count(1)}")
    print(f"  Replays (delta=0): {cc_deltas.count(0)}")
    print(f"  Drops (delta>1) : {sum(1 for d in cc_deltas if d > 1)}")
    print(f"  Out of order    : {sum(1 for d in cc_deltas if d < 0)}")

    print("\nFrameID")
    unique_ids = set(frame_ids)
    in_range = all(0x8000 <= f <= 0xBFFF for f in unique_ids)

    print(f"  Unique IDs      : {[hex(f) for f in unique_ids]}")
    print(f"  All in RT range : {'YES' if in_range else 'NO'}")

    print("\nFrame Length")
    unique_len = set(frame_lengths)

    print(f"  Unique lengths  : {unique_len}")
    print(f"  Fixed length    : {'YES' if len(unique_len) == 1 else 'NO'}")

    print(f"\n{'=' * 58}")

    checks = {
        "IAT mean within 0.5ms of 4ms target": abs(statistics.mean(iats_ms) - 4.0) < 0.5,
        "IAT std dev < 1.0ms": statistics.stdev(iats_ms) < 1.0,
        "No replay frames (delta=0)": cc_deltas.count(0) == 0,
        "No out-of-order frames": sum(1 for d in cc_deltas if d < 0) == 0,
        "All FrameIDs in valid RT range": in_range,
        "Fixed frame length": len(unique_len) == 1,
    }

    print("\nPass/Fail Summary")

    all_pass = True

    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {check}")

        if not result:
            all_pass = False

    if all_pass:
        print("\nAll checks passed.")
    else:
        print("\nSome checks failed — investigate before Week 5.")

verify()
