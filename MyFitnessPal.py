from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# MyFitnessPal Credentials
USERNAME = "orbarak"  # Use email instead of username
PASSWORD = "gtaabc922"

# Google Sheets Configuration
GOOGLE_SHEET_NAME = "Weight"  # Change this
CREDENTIALS_PATH = "path/to/your/credentials.json"  # Change this

# Function to log into MyFitnessPal
def login_myfitnesspal():
    driver = webdriver.Chrome()  # Initialize WebDriver
    driver.get("https://www.myfitnesspal.com/account/login")  # Open Login Page

    try:
        # Wait for email input field
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

        # Find password input field (update if necessary)
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        # Enter credentials
        email_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)

        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.url_contains("myfitnesspal.com")
        )

        print("✅ Successfully logged in!")
        return driver  # Return the Selenium WebDriver instance

    except Exception as e:
        print("❌ Login failed:", e)
        driver.quit()

# Function to extract today's macros
def get_macros(driver):
    driver.get("https://www.myfitnesspal.com/food/diary")  # Navigate to the diary page
    time.sleep(5)  # Allow page to load

    try:
        # Adjust these selectors based on MyFitnessPal's actual structure
        protein = driver.find_element(By.XPATH, "//td[contains(@class, 'protein-column')]").text
        carbs = driver.find_element(By.XPATH, "//td[contains(@class, 'carbs-column')]").text
        fats = driver.find_element(By.XPATH, "//td[contains(@class, 'fat-column')]").text
        calories = driver.find_element(By.XPATH, "//td[contains(@class, 'calories-column')]").text

        macros = {
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats,
            "Calories": calories
        }

        print("📊 Extracted Macros:", macros)
        return macros

    except Exception as e:
        print("❌ Error extracting macros:", e)
        return None

# Function to update Google Sheets
def update_google_sheets(macros):
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH)
    gs_client = gspread.authorize(creds)

    sheet = gs_client.open(GOOGLE_SHEET_NAME).sheet1  # Open the first sheet

    # Find the next empty row
    next_row = len(sheet.col_values(1)) + 1

    # Prepare row (matching your sheet structure)
    today = datetime.today().strftime('%d/%m/%y')
    data_row = [today, "", "", "", "", macros["Protein"], macros["Carbs"], macros["Fats"], macros["Calories"]]

    sheet.append_row(data_row)
    print(f"✅ Data successfully added to Google Sheets: {data_row}")

# Main Execution
def main():
    driver = login_myfitnesspal()  # Login to MyFitnessPal
    macros = get_macros(driver)  # Extract macros

    if macros:
        update_google_sheets(macros)  # Save to Google Sheets

    driver.quit()  # Close browser

if __name__ == "__main__":
    main()
