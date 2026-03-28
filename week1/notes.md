# Week 1 Notes — Binary Foundations & Python Networking

## Day 1 — 09-03-2026
**Hours logged today:** 2

## What I Did Today
- Created GitHub repository
- Set up local Git configuration and SSH key
- Created week1 folder structure

## Questions I Have
- How does Scapy handle raw socket permissions without root?


---------------------------------------------------------------



## Day 2 — 10-03-2026
**Hours logged:** 4

---

### Binary and Machine Code
- All data is stored in binary form in a computer (0s and 1s)
- CPU executes instructions on data in binary form
- Each binary digit is a bit, 8 bits = 1 byte
- Example: 01000001 in binary = 65 in decimal = letter 'A' in ASCII

### Principle of Duality
- The same binary pattern in memory can be interpreted as either 
  data or as an executable instruction depending on context
- A number like 0x41 can mean the integer 65, the letter 'A', 
  or part of a CPU instruction — same bits, different meaning
- This is foundational to memory exploitation: attackers abuse this 
  by injecting data that the CPU is tricked into executing as code
- Machine code and data are both stored in the same memory space 
  in binary form — there is no inherent separation between them

### Linux OS and Kali
- Linux is a family of free and open source operating systems 
  based on the Linux kernel
- Kali Linux is a distribution of Linux used for penetration testing
- Packages in Kali are imported from Debian repositories

### Kali Commands Learned
- ls        — list files in current directory
- ls -la    — list all files in long format
              -l shows permissions, owner, size, date
              -a shows hidden files (files starting with .)
- cd        — change directory
- pwd       — print working directory (shows where you currently are)
- mkdir     — make new directory
- rm        — remove file
- cat       — display file contents

### File Permissions
- Permission format: -rwxrwxrwx
- First character: d = directory, - = regular file, l = symbolic link
- Next 3 characters: owner permissions
- Next 3: group permissions
- Last 3: everyone else (others) permissions
- r = read, w = write, x = execute
- Example: -rwxr-xr--
  owner = rwx (can read, write, execute)
  group = r-x (can read and execute, cannot write)
  others = r-- (can only read)

### OverTheWire Bandit — Levels 0 to 4

- Bandit 0: ssh bandit0@bandit.labs.overthewire.org -p 2220
  Learned: SSH with custom port using -p flag

- Bandit 1: file named - in home directory
  Problem: cat - reads from stdin, not the file
  Solution: cat ./-
  Key learning: - means stdin in Linux, ./ forces it to be a filepath

- Bandit 2: filename has spaces
  Solution: cat "spaces in this filename"
  Key learning: quotes wrap filenames that contain spaces

- Bandit 3: hidden file inside inhere/
  Solution: cd inhere && ls -la
  Key learning: hidden files start with . and only show with -a flag

- Bandit 4: only one human-readable file among many
  Solution: file inhere/-file0*
  Key learning: file command identifies what type of data is in a file

### PicoCTF — Tab Tab Attack
- Used tab completion to navigate a deeply nested directory structure
- Key learning: pressing tab twice shows all possible completions 
  when there is ambiguity — useful for exploring unknown filesystems

---

## Questions I Still Have
- How does Scapy handle raw socket permissions without root?
- Is there a way to set Linux capabilities instead of running as sudo?

---

## What I Plan to Do Next
- Continue Linux Primer sections from Udemy course
- Start Bandit levels 5 onwards
- Begin looking at Python socket programming



-----





## Day 3 — 11-03-2026
**Hours logged:** 2

---

### What I Studied
- Intro to Hex (Udemy)
- Intro to Encoding and Base64 (Udemy)
- Linux Primer Two and Three (Udemy)
- Bandit levels 4 to 7 (OverTheWire)

---

### Key Things I Learned

#### Hexadecimal
- Hexadecimal is a base-16 number system
- Uses 0-9 for values 0-9 and A-F for values 10-15
- Each hex digit represents exactly 4 bits — called a nibble
- One byte (8 bits) = two hex digits
- Example: 00000000 to 11111111 in binary = 0 to 255 in decimal 
  = 00 to FF in hexadecimal
- This is why PROFINET's EtherType field is written as 0x8892 — 
  hex maps cleanly to bytes and is much more readable than binary

#### Hex Dump
- A hex dump is a hexadecimal representation of raw binary data 
  from memory, a file, or a storage device
- Used for debugging, reverse engineering, and digital forensics
- Shows data in three columns: memory offset on the left, 
  hex values in the middle, ASCII representation on the right
  where characters are printable
- More compact than binary — one byte shown as two hex digits 
  instead of eight binary digits

#### Base64
- Base64 encodes binary data into printable ASCII characters
- Used when binary data needs to travel through text-based systems 
  like email or HTTP headers that cannot handle raw binary
- Every 3 bytes of binary becomes 4 Base64 characters
- Recognized Base64 immediately in Bandit — several levels 
  use it to encode the password

#### Linux Commands Learned Today

- man — displays the manual for any command
  Example: man ls, man cat
  Usage: always check man before Googling a command

- file — identifies what type of data is inside a file
  Example: file readme → returns "ASCII text"
  Example: file ./-file01 → returns "data" (not human readable)
  Wildcards work: file ./-file* checks all files at once

- find — locates files by name, type, size, owner, and more
  Example: find ./ -name readme
  Example: find ./ -name "readme*" (wildcard)
  Example: find ./ -size 33c (c = bytes)
  Example: find ./ -user bandit7
  Parameters combine: find ./ -size 33c -user bandit7 -group bandit6
  Note: add 2>/dev/null to suppress permission denied errors

---

### Bandit Levels 4 to 7

- Bandit 4: find only human-readable file in inhere/ directory
  Files named -file00 through -file09
  Solution: file ./-file* — runs file command on all files at once
  Result: -file07 returned "ASCII text" — all others returned "data"
  Key learning: wildcards with file command let you check many 
  files simultaneously instead of one by one
  What I got stuck on: did not know ./-file* syntax would work 
  with wildcards. Had to look up the solution. Now understand that 
  * matches any characters after the prefix.

- Bandit 5: find file that is human-readable, 1033 bytes, 
  not executable
  Solution: find . -type f -size 1033c ! -executable
  Key learning: ! means NOT in find command — combining multiple 
  flags narrows the search precisely

- Bandit 6: file owned by user bandit7, group bandit6, 33 bytes,
  stored somewhere on the server
  Solution: find / -user bandit7 -group bandit6 -size 33c 2>/dev/null
  Key learning: searching from / searches the entire filesystem.
  2>/dev/null was essential — without it hundreds of 
  "Permission denied" errors flooded the output making 
  the result impossible to find

- Bandit 7: word next to "millionth" in data.txt
  Solution: grep "millionth" data.txt
  Key learning: grep searches inside file contents for a string — 
  far faster than reading a large file manually

---

### What Surprised Me Today

- The man command works on C language functions, not just 
  Linux commands. Running man gets shows the manual for the 
  C gets() function — and explicitly warns that gets() will 
  continue storing characters past the end of the buffer.
  This is directly relevant to Project 3 — gets() is one of 
  the most exploited functions in buffer overflow vulnerabilities.
  The vulnerability is literally documented in the manual.

- Wildcards work with the file command — file ./-file* checks 
  all matching files at once. Did not expect this to work 
  and it saved significant time on Bandit 4.

---

### Connections to the Project

- file command identifying ASCII vs binary data is the same 
  concept as feature extraction in Project 1 — distinguishing 
  normal from anomalous based on data properties
- man gets warning about buffer overflow connects directly 
  to Project 3 — gets() will be one of the vulnerable 
  functions I use to build my controlled test binary
- 2>/dev/null stderr suppression will be useful when running 
  Scapy scripts in Project 1 that generate permission warnings

---

### What I Did Not Complete Today
- Did not finish Python socket documentation reading
- Did not start port_scanner.py
- These move to Day 4

---

### Questions I Still Have
- Can find command search by file content, not just metadata?
- How does grep handle very large files efficiently?
- What exactly happens at the memory level when gets() 
  writes past the buffer end?

---

### What I Plan to Do Tomorrow
- Read Python socket documentation — focus on socket.socket(), 
  connect_ex(), and settimeout()
- Write port_scanner.py from scratch
- Continue Linux Primer Four from Udemy
- Attempt Bandit levels 8 and 9







## Day 4 — Linux Data Processing & Encoding

**Hours logged:** 2

---

###  Objective
- Understand how Linux handles data streams, filtering, and encoding
- Learn commands used for extracting and processing useful information from files

---

###  Concepts Learned

#### Standard Streams & Redirection
- `>` overwrites file content
- `>>` appends content to file
- Used to control output of commands

#### Text Processing Commands
- `grep` → search for patterns inside files
- `grep -i` → ignore case sensitivity
- `head` → first 10 lines
- `tail` → last lines

#### Command Chaining (Pipelines)
- `|` passes output of one command to another
- Example:
  - `cat file | grep string`
  - `cat file | sort | uniq -c | sort`

#### Binary Data Extraction
- `strings binaryfile | grep -i pico`
- Extracts readable text from binary files

#### File Management
- `mkdir`, `rm -r`, `cp`, `mv`

#### Compression & Archiving
- `zip` → creates compressed copy
- `zip -e` → password protected zip
- `unzip` → extract zip
- `gzip` → compresses and replaces original file
- `gunzip` → decompresses
- `tar -cf` → create archive
- `tar -xvf` → extract archive

#### Encoding & Utilities
- `base64` → encode/decode data
- `xxd` → binary to hex
- `tr` → character transformation

---

###  Implementation / Practice
- Used `grep` with files to filter specific strings
- Practiced command chaining:
  - `cat fasttrack.txt | sort | uniq -c`
- Extracted readable strings from binary:
  - `strings file | grep -i pico`
- Tried compression using `zip` and `gzip`

---

###  Observations
- Linux commands can be combined to form powerful data processing pipelines
- `grep` is significantly faster than manually searching large files
- Binary files are not completely unreadable — useful information can be extracted
- `gzip` removes original file while `zip` keeps it

---

###  Connections (to Project / Cybersecurity)
- `grep` + pipelines → similar to filtering data in IDS systems
- `strings` → useful in malware analysis and CTF challenges
- `base64` → commonly used in network protocols and data transfer
- Compression → relevant for storing packet captures and datasets

---

### Questions / Doubts
- How does `grep` efficiently search very large files?
- What algorithm is used in `gzip` compression?
- How does `strings` identify printable characters in binary?

---

###  Key Insights
- Linux CLI tools act as a lightweight data processing engine
- Small commands combined together can perform complex analysis
- Many cybersecurity tools rely on these same basic principles

---

### Ideas / Future Experiments
- Compare `grep` vs Python for searching large files
- Use `strings` on real executable files and analyze output
- Build a script that mimics basic `grep` functionality

---

### Next Steps
- Learn Python socket programming
- Build TCP client-server
- Start port scanner implementation







