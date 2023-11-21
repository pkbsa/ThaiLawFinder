import json
import re

# Read data from the input JSON file
with open('input.json', 'r', encoding='utf-8') as input_file:
    data = json.load(input_file)

# Function to remove all newline characters from a string
def remove_all_newlines(text):
    return re.sub(r'\n', ' ', text)

# Iterate through the data and remove all newline characters in the "chapter" and "addtitional" fields
for entry in data:
    entry["chapter"] = remove_all_newlines(entry["chapter"])
    entry["part"] = remove_all_newlines(entry["part"])
    entry["addtitional"] = remove_all_newlines(entry["addtitional"])

# Convert the JSON data into the desired format
formatted_data = [
    [entry["code"], entry["book"], entry["title"], entry["chapter"], entry["part"], entry["addtitional"]]
    for entry in data
]

# Write data to the output.txt file in the desired format
with open('output.txt', 'w', encoding='utf-8') as output_file:
    output_file.write("export const data = [\n")
    for entry in formatted_data:
        output_file.write("    " + "[" + ", ".join([f'"{value}"' for value in entry]) + "],\n")
    output_file.write("]")
