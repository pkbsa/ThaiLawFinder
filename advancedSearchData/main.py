import json

# Read data from the input JSON file
with open('input.json', 'r', encoding='utf-8') as input_file:
    data = json.load(input_file)

# Convert the JSON data into the desired format
formatted_data = [
    [entry["code"], entry["book"], entry["title"], entry["chapter"], entry["part"], entry["addtitional"]]
    for entry in data
]

# Write data to the output.txt file in the desired format
with open('output.txt', 'w', encoding='utf-8') as output_file:
    output_file.write("const data = [\n")
    for entry in formatted_data:
        output_file.write("    " + "[" + ", ".join([f'"{value}"' for value in entry]) + "],\n")
    output_file.write("]")
