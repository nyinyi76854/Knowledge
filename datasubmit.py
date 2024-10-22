import json
import sys
from datetime import datetime

# Get message and timestamp from GitHub Action input
message = sys.argv[1]
timestamp = sys.argv[2]

# Read existing data
try:
    with open('data.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    data = []

# Append new message and timestamp
new_entry = {
    "message": message,
    "timestamp": timestamp
}
data.append(new_entry)

# Write updated data back to JSON file
with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)
