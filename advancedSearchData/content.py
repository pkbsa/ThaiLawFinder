import csv
import os
from io import StringIO, TextIOWrapper

def addContent(csv_data) :
    js_file = 'static/js/data.js'
    txt_file = 'static/js/data.txt'

    # Rename the .js file to .txt
    os.rename(js_file, txt_file)

    # Read the data from the .txt file
    with open(txt_file, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Remove the first and last lines (which contain "export const data = [" and "];")
    existing_data = content[1:-1]

    # Read the CSV file and append the data
    existing_rows = set()

    reader = csv.DictReader(StringIO(csv_data))
    if csv_data.startswith('\ufeff'):
        csv_data = csv_data[1:]
    
    reader = csv.DictReader(StringIO(csv_data))
    
    for row in reader:
        # Convert the row to the desired format
        formatted_row = [
            row['code'],
            row['book'],
            row['title'],
            row['chapter'],
            row['part'],
            row['addtitional']
        ]
        # Convert the list to a tuple so it can be added to a set
        formatted_row_tuple = tuple(formatted_row)
        # Only append the row if it's not already in existing_rows
        if formatted_row_tuple not in existing_rows:
            existing_rows.add(formatted_row_tuple)
            existing_data.append("    " + str(formatted_row) + ",\n")
                
    # Write the data back to the .js file
    with open(js_file, 'w', encoding='utf-8') as file:
        file.write("export const data = [\n" + "".join(existing_data) + "];")


    # Delete the .txt file
    os.remove(txt_file)
    return "Added Content Successfully"

def removeContent(input_string) :
    js_file = 'static/js/data.js'
    txt_file = 'advancedSearchData/data.txt'

    # Rename the .js file to .txt
    os.rename(js_file, txt_file)

    # Read the data from the .txt file
    with open(txt_file, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Remove lines that contain the input string
    content = [line for line in content if input_string not in line]

    # Write the data back to the .txt file
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.writelines(content)

    # Rename the .txt file back to .js
    os.rename(txt_file, js_file)
    
    return "Successfully Removed from Content"