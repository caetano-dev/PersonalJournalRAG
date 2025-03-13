import csv
import re

# Input and output file names
input_file = "journal.txt"
output_file = "journal.csv"

# Regular expressions for detecting dates and timestamps
date_pattern = re.compile(r"^(\w{3} \d{1,2}, \d{4})$")
time_pattern = re.compile(r"^(\d{2}:\d{2}) - (.*)")

data = []
current_date = None

# Read and process the input file
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        # Check if the line is a date
        date_match = date_pattern.match(line)
        if date_match:
            current_date = date_match.group(1)
            continue

        # Check if the line is a timestamp entry
        time_match = time_pattern.match(line)
        if time_match and current_date:
            time = time_match.group(1)
            entry = time_match.group(2)
            data.append([current_date, time, entry])

# Write the extracted data to a CSV file
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Time", "Entry"])
    writer.writerows(data)

print(f"Journal successfully converted to {output_file}")
