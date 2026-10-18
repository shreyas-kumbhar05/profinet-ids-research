# This script is the foundation for traffic_generator/generator.py in Week 4.

from scapy.all import Ether, sendp, hexdump
import struct

def build_profinet_rt_frame(
    src_mac="08:00:27:a0:f4:9c",   # your Kali MAC — verify with: ip a
    dst_mac="01:0e:cf:00:00:00",   # PROFINET IO multicast — IEEE registered
    frame_id=0x8001,                # RT Class 1/2/3 — valid: 0x8000-0xBFFF
    cycle_counter=0,                # starts at 0, increments every cycle
    data_status=0x35,               # 0x35 = valid, running, no fault
    transfer_status=0x00,           # 0x00 = transfer valid
    payload_size=40                 # bytes of simulated cyclic IO data
):
    """
    Builds a minimal valid PROFINET RT frame.

    Frame layout after Ethernet header:
      Offset 0:  FrameID        (2 bytes, big-endian)
      Offset 2:  CycleCounter   (2 bytes, big-endian)
      Offset 4:  DataStatus     (1 byte)
      Offset 5:  TransferStatus (1 byte)
      Offset 6+: Cyclic IO data (payload_size bytes of zeros)
    """

    # Pack PROFINET RT header
    # > = big-endian
    # H = unsigned short (2 bytes)
    # B = unsigned byte  (1 byte)
    profinet_header = struct.pack(
        ">HHBB",
        frame_id,
        cycle_counter,
        data_status,
        transfer_status
    )

    # Simulated IO data — zeros represent no real PLC attached
    io_data = bytes(payload_size)

    # Full PROFINET payload = header + IO data
    full_payload = profinet_header + io_data

    # Wrap in Ethernet frame with EtherType 0x8892
    frame = Ether(
        src=src_mac,
        dst=dst_mac,
        type=0x8892
    ) / full_payload

    return frame


def inspect_frame(frame):
    """Print structured field breakdown and hex dump."""

    # Extract PROFINET fields from raw bytes
    payload = bytes(frame.payload)
    frame_id        = struct.unpack(">H", payload[0:2])[0]
    cycle_counter   = struct.unpack(">H", payload[2:4])[0]
    data_status     = payload[4]
    transfer_status = payload[5]

    print("=" * 55)
    print("PROFINET RT Frame — Field Inspection")
    print("=" * 55)
    print(f"  Src MAC        : {frame.src}")
    print(f"  Dst MAC        : {frame.dst}")
    print(f"  EtherType      : 0x{frame.type:04x}")
    print(f"  Total length   : {len(frame)} bytes")
    print()
    print(f"  FrameID        : 0x{frame_id:04x}  ({frame_id} decimal)")
    print(f"  CycleCounter   : {cycle_counter}")
    print(f"  DataStatus     : 0x{data_status:02x}  (binary: {data_status:08b})")
    print(f"  TransferStatus : 0x{transfer_status:02x}")
    print()
    print("--- Hex Dump ---")
    hexdump(frame)


def validate_frame(frame):
    """
    Validates the frame against PROFINET RT structural rules.
    Returns True if all checks pass.
    """
    payload = bytes(frame.payload)
    frame_id        = struct.unpack(">H", payload[0:2])[0]
    transfer_status = payload[5]

    checks = {
        "EtherType is 0x8892"          : frame.type == 0x8892,
        "Payload >= 6 bytes"           : len(payload) >= 6,
        "FrameID in RT range 0x8000-0xBFFF" : 0x8000 <= frame_id <= 0xBFFF,
        "TransferStatus is 0x00"       : transfer_status == 0x00,
        "Dst MAC is PROFINET multicast": frame.dst == "01:0e:cf:00:00:00",
    }

    print("--- Frame Validation ---")
    all_passed = True
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {check}")
        if not result:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    # Build frame
    frame = build_profinet_rt_frame()

    # Inspect
    inspect_frame(frame)
    print()

    # Validate
    passed = validate_frame(frame)
    print()

    if passed:
        print("All checks passed.")
        print("Frame is ready for Week 4 traffic generator.")
    else:
        print("One or more checks FAILED.")
        print("Fix before proceeding to Week 4.")

    # To send on your local interface — uncomment only when needed:
    # sendp(frame, iface="eth0", verbose=1)
