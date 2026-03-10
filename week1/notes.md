# Week 1 Notes — Binary Foundations & Python Networking

**Date:** 09-03-2026
**Hours logged today:** 2

## What I Did Today
- Created GitHub repository
- Set up local Git configuration and SSH key
- Created week1 folder structure

## Questions I Have
- How does Scapy handle raw socket permissions without root?


---------------------------------------------------------------


**Date:** 10-03-2026
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
