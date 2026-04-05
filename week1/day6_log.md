**Date:** 05/04/2026<br>
**Week:** Week 1<br>
**Day:** Day 6 <br>
**Hours Logged:** 1<br>

---

##  Objective
- Learn about python File I/O and CSU and also about DictWriter

---

##  Concepts Learned

### File I/O
- **What:** Helps in reading, writing from/to files in python
- **Why:** Helps to perform input/output operations

- **Where used:** Will be used in reading and writing CSV, pcap files (or more tasks as i learn them)



### CSV - Comma Separated Values
- **What:** Allows to put data into plain text files and seperate the fields using dilemeter like comma
- **Where used:** Will be used to store scan results, logs, etc
- **Code practiced:**
```bash
import csv

with open("file.txt", "r") as csv_file:
    reader = csv.reader()
    for row in reader:
        print(row)


with open("file.txt", "w") as csv_file:
    writer = csv.writer()
    writer.writerow(["port", "status"])
    writer.writerow([80, "open"])
```


### DictWriter
- **What:** DictWriter is a high level CSV that uses dictionaries instead of lists
- **Why:** Normal CSV file depends on position, we know what a certain column is about but not Python. DictWriter is key based, order doesn't matter and it is easy to extend
- **Where used:** It will be primarily used for storing data in much more strucutred form as the data will grow

```bash
import csv

with open("ports.csv", "w", newline="") as file:
    fieldnames = ["port", "status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({"port": 80, "status": "open"})
```



---

---

## 🧩 Challenges & Bugs
### Difficulty in understanding the difference between normal CSV and DictWriter 
- **What happened:** As conceptually both CSV and DictWriter are same, it was difficult to understand the key difference between them
- **How I fixed it:** Understood the concept using real world scenarios and also how using which will be more logical for my project




##  Next Steps
What you are doing tomorrow, based on what is left.
- Will be completing building the pcap scanner
- Update the notes.md with fully weekly log
