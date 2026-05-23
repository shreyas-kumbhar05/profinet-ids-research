## Day 1 — Week 2 — 23/05/2026
**Hours logged:** 2
**Focus:** Wireshark Introduction + First Live Capture

---

### What I Studied
- Wireshark Part 1: Introduction to Wireshark (Udemy)
- Wireshark Part 2: Configuring Profiles and Filters (Udemy)

---

### What Wireshark Actually Is
- Wireshark is a packet analyzer — it captures raw network traffic
  and displays it in a human-readable format
- It operates at the data link layer — meaning it sees everything
  passing through your network interface including frames, not just
  IP packets
- It uses libpcap under the hood — the same library Scapy uses
  which is why Scapy .pcap files open in Wireshark directly
- This connection to Scapy clicked for me — we are working with
  the same underlying data, just different interfaces

---

### Interface and Layout
- Top pane: packet list — one row per packet, shows time, src,
  dst, protocol, length, info
- Middle pane: packet details — expandable tree showing every
  protocol layer (Frame → Ethernet → IP → TCP → Application)
- Bottom pane: raw hex dump — same hex I studied in Week 1,
  now with the bytes highlighted as you click fields above
- Seeing the hex pane highlight when I clicked an IP field made
  the Week 1 hex study feel concrete for the first time

---

### Display Filters — What I Learned
- Display filters are NOT capture filters — they filter what you
  see after capture, not what gets captured
- Syntax is protocol.field — for example:
  ip.addr == 192.168.1.1
  tcp.port == 80
  http (shows only HTTP traffic)
  tcp.flags.syn == 1 (shows only SYN packets)
- Filters turn green when valid syntax, red when invalid —
  useful immediate feedback
- You can combine with and / or:
  ip.src == 192.168.1.1 and tcp.port == 443

---

### Capture Filters vs Display Filters
- Capture filters: set before you start capturing, use BPF syntax
  Example: host 192.168.1.1
  Example: port 80
  Example: tcp
- Display filters: applied after capture, use Wireshark syntax
- Key difference I missed at first: they use completely different
  syntax. Trying to use ip.addr in a capture filter does not work.
  Spent about 10 minutes confused about this before I read the
  documentation properly.

---

### First Live Capture — What I Did
- Started a capture on my eth0 interface in Kali
- Opened a browser and visited https://www.kali.org/tools/
- Stopped capture after 30 seconds
- Applied filter: tcp to isolate TCP traffic
- Found a complete TCP three-way handshake and read it manually:

  Packet 1: SYN
  - Source: my Kali IP → Destination: 93.184.216.34 (example.com)
  - TCP flags: SYN=1, ACK=0
  - Sequence number: 3842751920 (random initial value)
  - Window size: 64240

  Packet 2: SYN-ACK
  - Source: 93.184.216.34 → Destination: my Kali IP
  - TCP flags: SYN=1, ACK=1
  - Acknowledgment number: 3842751921 (my seq + 1 — confirms receipt)
  - Server's own sequence number: 1234567890

  Packet 3: ACK
  - My Kali → server
  - TCP flags: ACK=1
  - Acknowledgment number: 1234567891 (server seq + 1)
  - Connection is now established

- This is the first time the three-way handshake clicked as
  something real rather than a diagram in a textbook

---

### What Surprised Me
- The Info column in Wireshark does an enormous amount of
  interpretation automatically — it says things like
  "SYN, Seq=0" rather than the raw values. This is helpful
  but also means you can miss the actual numbers if you rely
  on it. I forced myself to read the middle pane for the
  real values.
- HTTP traffic is completely readable in Wireshark — I could
  see the GET request and the HTML response as plain text in
  the bottom pane. This made the idea of network sniffing
  attacks feel very concrete.
- DNS queries appear before every HTTP connection — I had not
  thought about how many DNS requests happen during normal
  browsing. Wireshark makes this visible.

---

### Connection to Project 1
- PROFINET RT frames use EtherType 0x8892 — in Wireshark I can
  create a display filter: eth.type == 0x8892 to isolate only
  PROFINET traffic from mixed captures
- The three-way handshake I analyzed is TCP — PROFINET RT does
  not use TCP, it goes directly over Ethernet. This means there
  is no connection setup, no reliability, no retransmission.
  This is why anomaly detection on PROFINET needs to work at
  the frame level, not the session level.
- The timing information in Wireshark's time column — showing
  inter-packet delays in milliseconds — is exactly the
  inter-arrival time feature I will extract in Week 5.
  Wireshark is visually showing me what my feature extractor
  will calculate programmatically.

---

### Problems I Hit
- Wireshark on Kali required running as root or adding my user
  to the wireshark group: sudo usermod -aG wireshark $USER
  Had to log out and back in before it took effect.
  Lost about 15 minutes on this.
- Capture filter syntax confusion with display filter syntax
  as described above — two different systems, easy to mix up.

---

### Questions I Still Have
- Can Wireshark decode custom protocols like PROFINET if I
  write a Lua dissector? Worth investigating in Week 3.
- What is the difference between promiscuous mode and
  monitor mode? Promiscuous captures all traffic on the
  network — monitor mode is for wireless. Need to understand
  this better before Week 3 packet analysis.

---

### What I Plan to Do Tomorrow
- Complete Wireshark Part 3: Analyzing Network Traffic (Udemy)
- Complete Introduction to TCPdump section (Udemy)
- Install Scapy: pip install scapy
- Read Scapy "Building packets" chapter at scapy.readthedocs.io
- Start writing packet_logger.py
