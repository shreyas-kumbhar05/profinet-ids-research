# traffic_generator/generator.py
# PROFINET RT cyclic traffic generator.
# Produces realistic baseline traffic at configurable cycle times.
#
# Usage:
#   sudo python3 traffic_generator/generator.py
#   sudo python3 traffic_generator/generator.py --cycle-time 2.0
#   sudo python3 traffic_generator/generator.py --duration 30

import time
import random
import struct
import argparse
import yaml
from scapy.all import Ether, conf


def load_config(path="traffic_generator/config.yaml"):
    """Load YAML config and return as dict."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_frame(config, cycle_counter):
    """
    Build one PROFINET RT Ethernet frame.
    Reuses frame construction logic from week3/profinet_frame.py.
    cycle_counter increments each call and wraps at 65535.
    """
    p = config["profinet"]
    g = config["generator"]

    # PROFINET RT header — big-endian
    header = struct.pack(
        ">HHBB",
        p["frame_id"],
        cycle_counter,
        p["data_status"],
        p["transfer_status"]
    )

    # Simulated IO data — fixed-length zeros
    payload = header + bytes(p["payload_size"])

    return Ether(
        src=g["src_mac"],
        dst=g["dst_mac"],
        type=g["ethertype"]
    ) / payload


def compute_jitter(std_ms, max_ms):
    """
    Gaussian jitter clipped to max_ms.
    Models realistic OS scheduling variance.
    """
    j = random.gauss(0, std_ms)
    return max(-max_ms, min(max_ms, j))


def print_stats(frames_sent, start_time, cycle_ms):
    """Print progress to terminal every log_interval frames."""
    elapsed = time.perf_counter() - start_time
    rate = frames_sent / elapsed if elapsed > 0 else 0
    expected = elapsed / (cycle_ms / 1000)

    print(
        f"  Frames: {frames_sent:>8} | "
        f"Elapsed: {elapsed:>6.1f}s | "
        f"Rate: {rate:>6.1f} fps | "
        f"Expected: {int(expected):>8}"
    )


def run_generator(config):
    """
    Main loop.
    Sends PROFINET RT frames with compensated timing.

    Compensated timing prevents long-term drift by scheduling
    transmissions relative to the original start time rather
    than the completion time of the previous frame.
    """

    t = config["timing"]
    c = config["capture"]
    g = config["generator"]

    cycle_ms = t["cycle_time_ms"]
    jitter_std = t["jitter_std_ms"]
    jitter_max = t["jitter_max_ms"]

    duration_s = c["duration_seconds"]
    log_interval = c["log_interval"]

    iface = g["interface"]

    cycle_ns = int(cycle_ms * 1_000_000)
    duration_ns = int(duration_s * 1_000_000_000)

    cycle_counter = 0
    frames_sent = 0

    start_perf = time.perf_counter()
    start_ns = time.perf_counter_ns()
    next_send_ns = start_ns

    # Persistent Layer-2 socket.
    # Reusing a single socket avoids the large overhead of repeatedly
    # opening sockets through sendp() on every iteration.
    l2_socket = conf.L2socket(iface=iface)

    print(f"\nPROFINET Traffic Generator")
    print(f"  Interface  : {iface}")
    print(f"  Cycle time : {cycle_ms}ms  ({1000 / cycle_ms:.0f} fps)")
    print(f"  Jitter std : {jitter_std}ms")
    print(f"  Duration   : {duration_s}s")
    print(f"  Est frames : {int(duration_s / (cycle_ms / 1000))}")
    print("\nRunning...\n")

    try:
        while True:

            if time.perf_counter_ns() - start_ns >= duration_ns:
                break

            frame = build_frame(config, cycle_counter)
            l2_socket.send(frame)

            frames_sent += 1
            cycle_counter = (cycle_counter + 1) % 65536

            if frames_sent % log_interval == 0:
                print_stats(frames_sent, start_perf, cycle_ms)

            # Compensated timing
            jitter_ns = int(compute_jitter(jitter_std, jitter_max) * 1_000_000)

            next_send_ns += cycle_ns + jitter_ns
            sleep_ns = next_send_ns - time.perf_counter_ns()

            if sleep_ns > 0:
                time.sleep(sleep_ns / 1_000_000_000)

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")

    finally:
        l2_socket.close()

    elapsed = time.perf_counter() - start_perf
    actual_fps = frames_sent / elapsed if elapsed > 0 else 0

    print("\nComplete.")
    print(f"  Total frames : {frames_sent}")
    print(f"  Total time   : {elapsed:.2f}s")
    print(f"  Actual FPS   : {actual_fps:.1f}")
    print(f"  Expected FPS : {1000 / cycle_ms:.1f}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="PROFINET RT traffic generator"
    )

    parser.add_argument(
        "--config",
        default="traffic_generator/config.yaml"
    )

    parser.add_argument(
        "--cycle-time",
        type=float,
        help="Cycle time in milliseconds"
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="Duration in seconds"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    config = load_config(args.config)

    if args.cycle_time:
        config["timing"]["cycle_time_ms"] = args.cycle_time

    if args.duration:
        config["capture"]["duration_seconds"] = args.duration

    run_generator(config)
