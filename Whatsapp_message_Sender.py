from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import date
import pyodbc  # You forgot to import this
import requests

# Function to send the message
def send_message(url, driver):
    driver.get(url)
    try:
        sleep(5)  # Wait for page to load

        # Click 'Continue to Chat' button
        continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue to Chat']")
        continue_btn.click()
        sleep(3)

        # Click 'use WhatsApp Web' button
        use_web_btn = driver.find_element(By.XPATH, "//span[text()='use WhatsApp Web']")
        use_web_btn.click()
        sleep(10)  # Wait for WhatsApp Web to load and QR scan if needed

        # Click the send button
        send_btn = driver.find_element(By.XPATH, "//span[@data-icon='send']")
        send_btn.click()
        sleep(5)

    except Exception as e:
        print(f"Error: {e}")

# Function to update flag in the database
def update_flag(cursor, phone_number):
    update_query = f"UPDATE Attendance_table SET Flag = 1 WHERE Phn_Number = '{phone_number}'"
    cursor.execute(update_query)
    cursor.commit()

# Connect to SQL Server
server = 'Karthikeyan'
database = 'Attendance'
username = 'sa'
password = '123'

# Establish connection
cnxn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)
cursor = cnxn.cursor()

if cursor:
    print("Connected successfully")

# Today's date
today_date = date.today().strftime('%Y-%m-%d')
query = f"SELECT Phn_Number, Message, Flag FROM Attendance_table WHERE Date = '{today_date}'"
cursor.execute(query)

# Chrome profile setup
chrome_profile_path = "C:/Users/HP/AppData/Local/Google/Chrome/User Data"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
chrome_options.add_argument("profile-directory=Profile 12")

# Launch Chrome
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Process rows
rows = cursor.fetchall()
for row in rows:
    phone_number = row.Phn_Number
    message = row.Message
    if row.Flag == 1:
        continue

    # Generate WhatsApp message URL
    message_encoded = message.replace(' ', '%20')
    url = f"https://api.whatsapp.com/send/?phone={phone_number}&text={message_encoded}&type=phone_number&app_absent=0"

    send_message(url, driver)
    update_flag(cursor, phone_number)

# Cleanup
driver.quit()
cursor.close()
cnxn.close()
