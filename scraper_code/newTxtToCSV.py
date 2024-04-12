import re
import csv

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

def process_file(param_code):

    # Read the content of input.txt
    with open('static/input.txt', 'r', encoding='utf-8') as input_file:
        input_text = input_file.read()

    # Remove brackets and numbers inside brackets
    input_text = thai_to_arabic(re.sub(r'\[(\d+|๐-๙+)\]', '', input_text))
    #print(input_text)

    # Replace Thai numbers with Arabic numerals
    input_text = thai_to_arabic(input_text)

    # Split the input_text into lines
    lines = input_text.split('\n')
    # Remove leading whitespaces from each line
    lines = [line.lstrip() for line in lines]
    # Join the lines back into a single string
    input_text = '\n'.join(lines)

    # Split the text into "มาตรา" and "information" using regular expressions
    pattern = r'(มาตรา\s\d+[/\d+]*)\s(.*?)(?=\nมาตรา\s\d+[/\d+]*|\Z)|^(ภาค|หมวด|ลักษณะ)'
    data = []

    code = param_code
    book = '-'
    title = '-'
    chapter = '-'
    part = '-'
    addtitional = '-'

    pending_replacements = {}

    # Find the first occurrence of 'มาตรา'
    match_position = input_text.find('มาตรา')
    if match_position != -1:
        # Get the text before 'มาตรา'
        text_before_match = input_text[:match_position].strip()
        if '\nภาคที่' in text_before_match or '\nภาค' in text_before_match:
            parts = text_before_match.split('\nภาคที่', 1) if '\nภาคที่' in text_before_match else text_before_match.split('\nภาค', 1)
            book = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
            title = '-'
            chapter = '-'
            part = '-'
            addtitional = '-'
            if '\nลักษณะที่' in parts[1] or '\nลักษณะ' in parts[1]:
                parts = parts[1].split('\nลักษณะที่', 1) if '\nลักษณะที่' in parts[1] else parts[1].split('\nลักษณะ', 1)
                book = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                title = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
                if '\nหมวดที่' in parts[1] or '\nหมวด' in parts[1]:
                    parts = parts[1].split('\nหมวด', 1)
                    title = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                    chapter = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
                    if '\nส่วนที่' in parts[1] or '\nส่วน' in parts[1]:
                        parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                        chapter = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                        part = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')

        elif '\nลักษณะที่' in text_before_match or '\nลักษณะ' in text_before_match:
            parts = text_before_match.split('\nลักษณะที่', 1) if '\nลักษณะที่' in text_before_match else text_before_match.split('\nลักษณะ', 1)
            title = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
            chapter = '-'
            part = '-'
            addtitional = '-'
            if '\nหมวดที่' in parts[1] or '\nหมวด' in parts[1]:
                parts = parts[1].split('\nหมวดที่', 1) if '\nหมวดที่' in parts[1] else parts[1].split('\nหมวด', 1)
                title = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                chapter = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
                if '\nส่วนที่' in parts[1] or '\nส่วน' in parts[1]:
                    parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                    chapter = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                    part = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')

        elif '\nหมวดที่' in text_before_match or '\nหมวด' in text_before_match:
            parts = text_before_match.split('\nหมวดที่', 1) if '\nหมวดที่' in text_before_match else text_before_match.split('\nหมวด', 1)
            chapter = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')
            part = '-'
            addtitional = '-'
            if '\nส่วนที่' in parts[1] or '\nส่วน' in parts[1]:
                parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                chapter = add_brackets_around_number(parts[0].strip()).replace('\n', ' ')
                part = add_brackets_around_number(parts[1].strip()).replace('\n', ' ')

        elif '\nส่วนที่' in text_before_match or '\nส่วน' in text_before_match:
            part = add_brackets_around_number(text_before_match.split('\nส่วนที่', 1) if '\nส่วนที่' in text_before_match[1] else text_before_match[1].split('\nส่วน', 1)[1].strip()).replace('\n', ' ')
            addtitional = '-'

    i = 0
    for match in re.finditer(pattern, input_text, re.DOTALL):
        i += 1
        section = match.group(1).replace('\n', ' ')
        detail = match.group(2).strip()
        #print(detail)
        # Check if detail starts with one of the specified words
        words_to_check = ["ทวิ", "ตรี", "จัตวา", "เบญจ", "ฉ", "สัตต", "อัฏฐ", "นว", "ทศ", "เอกาทศ", "ทวาทศ", "เตรส", "จตุทศ", "ปัณรส", "โสฬส", "สัตตรส"]
        for word in words_to_check:
            if '\nภาคที่ ' in detail or '\nภาค ' in detail:
                parts = detail.split('\nภาคที่', 1) if '\nภาคที่' in detail else detail.split('\nภาค', 1)
                detail = parts[0]
                pending_replacements['book'] = add_brackets_around_number(parts[1].strip())
                pending_replacements['title'] = '-'
                pending_replacements['chapter'] = '-'
                pending_replacements['part'] = '-'
                pending_replacements['addtitional'] = '-'
                if '\nลักษณะที่ ' in parts[1] or '\nลักษณะ ' in parts[1]:
                    parts = parts[1].split('\nลักษณะที่', 1) if '\nลักษณะที่' in parts[1] else parts[1].split('\nลักษณะ', 1)
                    pending_replacements['book'] = add_brackets_around_number(parts[0].strip())
                    pending_replacements['title'] = add_brackets_around_number(parts[1].strip())
                    if '\nหมวดที่ ' in parts[1] or '\nหมวด ' in parts[1]:
                        parts = parts[1].split('\nหมวดที่', 1) if '\nหมวดที่' in parts[1] else parts[1].split('\nหมวด', 1)
                        pending_replacements['title'] = add_brackets_around_number(parts[0].strip())
                        pending_replacements['chapter'] = add_brackets_around_number(parts[1].strip())
                        if '\nส่วนที่ ' in parts[1] or '\nส่วน ' in parts[1]:
                            parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                            pending_replacements['chapter'] = add_brackets_around_number(parts[0].strip())
                            pending_replacements['part'] = add_brackets_around_number(parts[1].strip())

            elif '\nลักษณะที่ ' in detail or '\nลักษณะ ' in detail:
                parts = detail.split('\nลักษณะที่', 1) if '\nลักษณะที่' in detail else detail.split('\nลักษณะ', 1)
                detail = parts[0]
                pending_replacements['title'] = add_brackets_around_number(parts[1].strip())
                pending_replacements['chapter'] = '-'
                pending_replacements['part'] = '-'
                pending_replacements['addtitional'] = '-'
                if '\nหมวดที่ ' in parts[1] or '\nหมวด ' in parts[1]:
                    parts = parts[1].split('\nหมวดที่', 1) if '\nหมวดที่' in parts[1] else parts[1].split('\nหมวด', 1)
                    pending_replacements['title'] = add_brackets_around_number(parts[0].strip())
                    pending_replacements['chapter'] = add_brackets_around_number(parts[1].strip())
                    if '\nส่วนที่ ' in parts[1] or '\nส่วน ' in parts[1]:
                        parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                        pending_replacements['chapter'] = add_brackets_around_number(parts[0].strip())
                        pending_replacements['part'] = add_brackets_around_number(parts[1].strip())
            elif '\nหมวดที่ ' in detail or '\nหมวด ' in detail:
                parts = detail.split('\nหมวดที่', 1) if '\nหมวดที่' in detail else detail.split('\nหมวด', 1)
                detail = parts[0]
                pending_replacements['chapter'] = add_brackets_around_number(parts[1].strip())
                pending_replacements['part'] = '-'
                pending_replacements['addtitional'] = '-'
                if '\nส่วนที่ ' in parts[1] or '\nส่วน ' in parts[1]:
                    parts = parts[1].split('\nส่วนที่', 1) if '\nส่วนที่' in parts[1] else parts[1].split('\nส่วน', 1)
                    pending_replacements['chapter'] = add_brackets_around_number(parts[0].strip())
                    pending_replacements['part'] = add_brackets_around_number(parts[1].strip())
            elif '\nส่วนที่ ' in detail or '\nส่วน ' in detail:
                parts = detail.split('\nส่วนที่', 1) if '\nส่วนที่' in detail else detail.split('\nส่วน', 1)
                detail = parts[0]
                pending_replacements['part'] = add_brackets_around_number(parts[1].strip())
                pending_replacements['addtitional'] = '-'
                
            if detail.startswith(word):
                # Append the word to section and remove it from detail
                #print(word)
                section += " " + word
                detail = detail[len(word):].strip()
            
        if "ผู้รับสนองพระบรมราชโองการ" in detail:
            detail = detail.split("ผู้รับสนองพระบรมราชโองการ")[0].strip()
            
        data.append((code, section, book, title, chapter, part, addtitional, detail, i))
        #print(code, section, book, title, chapter, part, addtitional, detail, i)
        
        # Apply pending replacements in the next iteration
        if pending_replacements:
            book = pending_replacements.get('book', book).replace('\n', ' ')
            title = pending_replacements.get('title', title).replace('\n', ' ')
            chapter = pending_replacements.get('chapter', chapter).replace('\n', ' ')
            part = pending_replacements.get('part', part).replace('\n', ' ')
        
        if "ผู้รับสนองพระบรมราชโองการ" in match.group(2):
            break

    # Write the data to a CSV file with UTF-8 encoding
    with open('static/output.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['code','section','book','title','chapter','part','addtitional', 'detail','section_sort'])  # Write header
        csv_writer.writerows(data)

    print("Data has been saved to 'output.csv'")

if __name__ == '__main__':
    process_file("test")