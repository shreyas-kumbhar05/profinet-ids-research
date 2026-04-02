**Date:** 02/04/2026
**Week:**Week 1
**Day:** Day 5 
**Hours Logged:** 2

---

##  Objective
- Today I have decided to complete the networking basic module
- Also, I am planning to learn and build a port scanner by myself

---

##  Concepts Learned

### Intro to Computer Networks
- Computer network is a set of computers sharing resources located on network nodes. Common nodes includes servers, personal computers, network devices, etc
- Computer network allows devices over a network to share information with each other
- Computers uses common communication protocols over digital interconnections to communicate with each others
- In my project, computer networks will be the core of the research and will be needed throughout the project

### Internet (Expansion of computer networks)
- Internet is a system of interconnected computer networks that uses the internet protocol suites i.e., TCP/IP to communicate between networks and devices. 
- It is a network that consists of private, public, educational, government networks linked with broad number of electronic, wireless and optical networkin devices\
- A Local Area Network (LAN) is a computer network that interconnects devices within a small residence are such as scholl, laboratory, campus, offices

### IP Address(IPv4)
- IP Address is a numerical label used to find a node on the network using IP communication protocol
- Finding a device in the network using name would almost be impossible. IP addresses helps us in finding a device easily by assinging it with an IP address
- IPv4 is a 32bit/4 bytes address. There are 4 octets, each octet containing 8 bits which makes the 32 bits. Decimal dot(.) notation is used  to make the IP address readable to humans. Example of deciamal dot notation: 192.161.128.142

- In IPv4, a network can be also categorized by its subnet mask which is a bitmask that when applied with a bitwise AND operation on any IP address in the network gives us the network address
- To get the network address:
1. Take the decimal dot notation of the IP address (142.250.191.142)
2. Convert it to its binary form (10001110, 11111010, 10111111, 10001110)
3. Take thet subnet mask (255.255.255.0) convert it into its binary form
4. Perform bitwise AND operation we get the network address and the host identifier: 
- Network address: 142.250.191.0
- Host identifier: 0.0.0.142

---
- IPv4 has 5 Network Address Classes:
5. Class A: Leading bit: 0
					Start address: 0.0.0.0, end address: 127.255.255.255
					Default subnet masks:  255.0.0.0
6.  Class B: Leading bit: 10
					Start address: 128.0.0.0, end address: 191.255.255.255
					Default subnet masks:  255.255.0.0
5. Class C: Leading bit: 110
					Start address: 192.0.0.0, end address: 223.255.255.255
					Default subnet masks:  255.255.255.0
5. Class D: Leading bit: 1110
					Start address: 224.0.0.0, end address: 239.255.255.255
					Default subnet masks: not defined
5. Class E: Leading bit: 1111
					Start address: 240.0.0.0, end address: 255.255.255.255
					Default subnet masks:  Not defined


### Port
- Port number is a number assigned to uniquely identify a connection endpoint 	and to direct data to a specific service
- Example: 142.250.191.142: 443. 443 is the port number fo HTTPS

### Localhost 
- Localhost refers to the current computer used to access it, it is reserved for loopback purposes.
- It is used to access the network services that are running on the host via the loopback network interface

### Broadcast address
- It is a network address used to transmit to all devices connected to the network
- To find broadcast address: find the network address and subnet mask, compute the bit complement of the subnet mask, perform bitwise OR between network address and bit complement.
- Used: >ip a | grep -A3 docker, found the broadcasting address
---

##  Implementation

### Portscanner
- **What I built:**  Built a port scanner that scans for any open ports, found 0 after running it
- **How it works:** We use the socket library in python along with its build-in functions like socket.socket(), connect_ex()
- **Command to run it:**
```bash
cd ~/profinet-ids-research/week1
python3 port_scannner.py
```
- **Output I got:**
```
Scanning 127.0.0.1...
Scan complete. 0 open ports found.

```
- **Problems I hit:** The main problem was to understand the concepts of sockets.
- **How I fixed them:** Solved it by refering python docs on socket and also watching youtube videos on developing socket in python.

---


##  Observations

- The power of python suprised me, how just a few lines of code helped me finding any open ports which might have taken a lot to write it in C or C++

---

##  Connections
### To the Project
- Everything i learned from computer networks to port scanner will help me in the future when i'll actually build the IDS system. These concepts will act like the basics for the upcoming project

---

##  Open Questions

- Wasn't able to build the port scanner on my own needed help from youtube videos, need to revisit and learn how to build it on my own without any external help

---
##  Next Steps
- Tomorrow, I plan to learn more about python file I/O and CSV
- Also building a pcap Reader with dpkt
