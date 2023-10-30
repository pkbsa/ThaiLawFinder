import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape data from a page using BeautifulSoup
def scrape_data_with_beautifulsoup(page_url):
    try:
        # Send a GET request to the URL
        response = requests.get(page_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the <ul> element with class 'nav-search'
            ul_element = soup.find('ul', class_='nav-search')

            # Initialize lists to store titles, details, and texts
            titles = []
            details = []
            texts = []

            # Initialize a variable to keep track of the previous text
            prev_text = None

            # Find all <li> elements with class 'clear result' within the <ul>
            li_elements = ul_element.find_all('li', class_='clear result')

            for li in li_elements:
                # Find the <label> element
                label_element = li.find('label', class_='css-label med elegant content-title')

                # Extract the value from the hidden input within the <label>
                if label_element:
                    hidden_input = label_element.find('input', type='hidden')
                    if hidden_input:
                        title = hidden_input['value'].strip()
                        titles.append(title)

                # Find the second <p> element inside the <li> element
                detail_element = li.find('li', class_='item_short_text content-detail')
                if detail_element:
                    second_p_element = detail_element.find_all('p', class_='content-detail')[1] if len(
                        detail_element.find_all('p', class_='content-detail')) > 1 else None

                    # Try to extract the detail text; if the second <p> element doesn't exist, use the first one
                    if second_p_element:
                        detail_text = second_p_element.text.strip()
                    else:
                        first_p_element = detail_element.find('p', class_='content-detail')
                        detail_text = first_p_element.text.strip()
                    details.append(detail_text)

                # Find all <li class="text-option"> elements and concatenate them with "|"
                text_option_elements = li.find_all('li', class_='text-option')

                # Extract and append the concatenated text to the list with a new line if different from the previous text
                if text_option_elements:
                    text = ' | '.join([text_element.text.strip() for text_element in text_option_elements])
                    if text != prev_text:
                        texts.append(text)
                        prev_text = text

            return titles, details, texts
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None, None, None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None, None

# Function to save data to a CSV file
def save_to_csv(file_path, data):
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:  # Check if the file is empty
            writer.writerow(["Title", "Detail", "Text"])
        for row in data:
            writer.writerow(row)

# Specify the base URL for the pages
base_url = "http://deka.supremecourt.or.th/search/index/"

# Loop through page numbers from 1 to 6580
for page_number in range(1, 6581):
    page_url = f"{base_url}{page_number}"
    scraped_data = scrape_data_with_beautifulsoup(page_url)

    if all(scraped_data):  # Check if all values are not None
        non_none_data = [data for data in scraped_data if data is not None]
        data = list(zip(*non_none_data))  # Transpose the list
        save_to_csv("scraped_data.csv", data)
        print(f"Data from page {page_number} saved to 'scraped_data.csv'")
    else:
        print(f"No data found on page {page_number}")
