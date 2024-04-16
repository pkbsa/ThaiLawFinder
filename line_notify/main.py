import pymysql
import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Connect to the database
def main():

    connection = pymysql.connect(host='db4free.net',
                                user='netgluayadmin',
                                password='netgluay',
                                database='netgluaydb')

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Setup Selenium webdriver
    webdriver_service = Service(ChromeDriverManager().install())

    # SQL query to fetch records
    sql = "SELECT id, name, copy, status, date, url FROM law"

    summary_str = ''
    success_count = 0
    error_count = 0

    line_api = 'Eowx3XT2qK5FJf0PQ5BRdFJM80b5hIDx6l55OZ4uEOn'
    payload = '\n'

    try:
        with connection.cursor() as cursor:
            # Execute the SQL query
            cursor.execute(sql)
            
            # Fetch all the rows
            rows = cursor.fetchall()
            
            # Iterate over each row
            for row in rows:
                id, name, copy, status, date, url = row
                
                # Visit the URL
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                
                # Wait for the page to load
                WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.fw-bold')))
                time.sleep(5)
                
                # Extract information from the webpage
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                div = soup.find('div', {'class': 'row'})
                spans = div.find_all('span', {'class': 'ng-star-inserted'})
                
                # Extract name, copy, status, and date from the spans
                name_text = spans[0].text.strip().split(':')[-1].strip()  # Extract name and remove preceding characters
                copy_text = spans[1].text.strip().split(':')[-1].strip()  # Extract copy and remove preceding characters
                status_text = spans[2].text.strip().split(':')[-1].strip()  # Extract status and remove preceding characters
                date_text = spans[3].text.strip().split(':')[-1].strip()  # Extract date and remove preceding characters
                
                # Compare the extracted information with the information in your database
                # print("-name : " + name_text +" (expected : "+ name +")")
                # print("-copy : " + copy_text +" (expected : "+ copy +")")
                # print("-status : " + status_text +" (expected : "+ status +")")
                # print("-date : " + date_text +" (expected : "+ date +")")

                if name_text == name and copy_text == copy and status_text == status and date_text == date:
                    success_count += 1
                    current_status = 1  # Information is up-to-date
                    print("✅ " + name + "(up-to-date)")
                    payload += "✅ " + name + "(up-to-date)\n"

                else:
                    error_count += 1
                    current_status = 0  # Information is not up-to-date
                    print("❌ " + name + "(outdated)")
                    payload += "❌ " + name + "(outdated)\n"

                    if name_text != name :
                        print("- ❌ ชื่อ : " + name_text +" (expected : "+ name +")")
                        payload += "- ชื่อ : " + name_text +" (expected : "+ name +")\n"
                    if copy_text != copy :
                        print("- ❌ ฉบับ : " + copy_text +" (expected : "+ copy +")")
                        payload += "- ฉบับ : " + copy_text +" (expected : "+ copy +")\n"
                    if status_text != status :
                        print("- ❌ สถานะ : " + status_text +" (expected : "+ status +")")
                        payload += "- สถานะ : " + status_text +" (expected : "+ status +")\n"
                    if date_text != date :
                        print("- ❌ วันที่ : " + date_text +" (expected : "+ date +")")
                        payload += "- วันที่ : " + date_text +" (expected : "+ date +")\n"
                
                # Update the currentStatus column in the database
                update_sql = "UPDATE law SET currentStatus = %s WHERE id = %s"
                cursor.execute(update_sql, (current_status, id))
                connection.commit()
                driver.quit()


    finally:
        # Close the database connection and the WebDriver
        payload_summary = ''
        print("Total Items Reviewed:", int(success_count) + int(error_count))
        print("Up-to-dated Items : ", int(success_count))
        print("Outdated Items: ", int(error_count))

        payload_summary += f"\nTotal Items Reviewed: {int(success_count) + int(error_count)}"
        payload_summary += f"\nUp-to-date Items: {int(success_count)}"
        payload_summary += f"\nOutdated Items: {int(error_count)}"
        

    if line_api != None :

        headers = {
            'Authorization': f'Bearer {line_api}'
        }

        data = {
            'message': payload,
            'access_token': line_api
        }

        data_summary = {
            'message': payload_summary,
            'access_token': line_api
        }

        response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data_summary)
        response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)

        # Handle response
        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print("Failed to send notification")

        connection.close()
        
if __name__ == "__main__":
    main()