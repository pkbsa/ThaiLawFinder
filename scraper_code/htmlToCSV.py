import re
import csv
from bs4 import BeautifulSoup
import chardet

def add_brackets_around_number(text):
    # Use regular expression to find brackets before and after numbers
    # and add brackets around the number
    result = re.sub(r'(\()*(\d+)(\))*(?=\s|$)', r'(\2)', text)
    return result

# Define a function to convert Thai numbers to Arabic numerals
def thai_to_arabic(text):
    # Define a dictionary for Thai to Arabic numeral conversion
    thai_to_arabic_dict = {
        '๐': '0',
        '๑': '1',
        '๒': '2',
        '๓': '3',
        '๔': '4',
        '๕': '5',
        '๖': '6',
        '๗': '7',
        '๘': '8',
        '๙': '9'
    }

    # Use a regular expression to find and replace Thai numbers
    for thai_num, arabic_num in thai_to_arabic_dict.items():
        text = text.replace(thai_num, arabic_num)

    return text

# Detect the encoding of the local HTML file
encoding_info = chardet.detect(open('./test/getfile.html', 'rb').read())

# Load the local HTML file with detected encoding
with open('./test/getfile.html', 'r', encoding=encoding_info['encoding']) as html_file:
    html_content = html_file.read()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract the text from the HTML page
input_text = soup.get_text()
input_text = thai_to_arabic(re.sub(r'\[(\d+|๐-๙+)\]', '', input_text))

# Extract the text from the second and third lines
lines = soup.find_all('p', class_='MsoNormal')
code = lines[1].get_text(strip=True) + " (" + lines[2].get_text(strip=True) + ")"
code = re.sub(r'\[(\d+|๐-๙+)\]', '', code)
code = thai_to_arabic(code)

# Split the text into "มาตรา" and "information" using a simpler pattern
pattern = r'(มาตรา\s\d+[/\d+]*)\s(.*?)(?=\nมาตรา\s\d+[/\d+]*|\Z)'
data = []

book = '-'
title = '-'
chapter = '-'
part = '-'
additional = '-'

i = 0
for match in re.finditer(pattern, input_text, re.DOTALL):
    i += 1
    section = match.group(1).replace('\n', ' ')
    detail = match.group(2).strip()

    # Check if detail starts with one of the specified words
    words_to_check = ["ทวิ", "ตรี", "จัตวา", "เบญจ", "ฉ"]
    for word in words_to_check:
        if 'ภาค ' in detail:
            detail,book = detail.split('ภาค', 1)
            book = book.strip()
            detail = detail.lstrip(' ')
            book = add_brackets_around_number(book.replace('\n', ' '))
            title = '-'
            chapter = '-'
            part = '-'
            additional = '-'
        if 'ลักษณะ ' in detail:
            detail,title = detail.split('ลักษณะ', 1)
            title = title.strip()
            detail = detail.lstrip(' ')
            title = add_brackets_around_number(title.replace('\n', ' '))
            chapter = '-'
            part = '-'
            additional = '-'
        if 'หมวด ' in detail:
            detail,chapter = detail.split('หมวด', 1)
            chapter = chapter.strip() 
            detail = detail.lstrip(' ') 
            chapter = add_brackets_around_number(chapter.replace('\n', ' '))
            part = '-'
            additional = '-'
        if 'ส่วน ' in detail:
            print(detail)
            detail,part = detail.split('\n ส่วน', 1)
            part = part.strip()  
            detail = detail.lstrip(' ')  
            part = add_brackets_around_number(part.replace('\n', ' '))
            additional = '-'

        if detail.startswith(word):
            # Append the word to section and remove it from detail
            section += " " + word
            detail = detail[len(word):].strip()
            
    if "ผู้รับสนองพระบรมราชโองการ" in detail:
        detail = detail.split("ผู้รับสนองพระบรมราชโองการ")[0].strip()
        
    data.append((code, section, book, title, chapter, part, additional, detail, i))
    print(code, section, book, title, chapter, part, additional, detail, i)
    
    if "ผู้รับสนองพระบรมราชโองการ" in match.group(2):
        break

# Write the data to a CSV file with UTF-8 encoding
with open('output-html.csv', 'w', newline='', encoding='utf-8-sig') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['code','section','book','title','chapter','part','additional', 'detail','section_sort'])  # Write header
    csv_writer.writerows(data)

print("Data has been saved to 'output-html.csv'")
