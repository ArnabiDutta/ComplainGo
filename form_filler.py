from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select # Needed for the dropdown
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import time
import os

# --- THIS IS THE ONLY FUNCTION THAT NEEDS CHANGES ---
def submit_to_replica_form(user_details, complaint_details):
    """
    Automates filling our replica of the PWD complaint form hosted on Netlify.
    """
    
    FORM_URL = "https://aesthetic-bunny-3b2ef2.netlify.app/"
    
    # --- CHANGE #1: Add the necessary Chrome options for the server ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        
        # --- CHANGE #2: Pass the 'options' to the driver ---
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(FORM_URL)
        time.sleep(2) # Wait for the page to load
        
        #
        # --- NO OTHER CHANGES ARE NEEDED BELOW THIS LINE ---
        # The logic for finding and filling elements is correct.
        #
        
        # 1. Fill Text Inputs by their ID
        driver.find_element(By.ID, "ContactNo").send_keys(user_details["phone"])
        driver.find_element(By.ID, "ComplainantName").send_keys(user_details["name"])
        driver.find_element(By.ID, "ComplaintLocation").send_keys("AI Generated Location Placeholder")
        driver.find_element(By.ID, "ComplaintComment").send_keys(complaint_details["description"])
        
        # 2. Select from the Dropdown menu by its value
        category_map = {"Damaged Road": "4", "Water Logging": "2", "Streetlight": "1"}
        select_element = Select(driver.find_element(By.ID, "ComplaintType"))
        value_to_select = category_map.get(complaint_details["category"], "4")
        select_element.select_by_value(value_to_select)
        
        # 3. Upload the Image by its ID
        file_input = driver.find_element(By.ID, "Image")
        absolute_image_path = os.path.abspath(complaint_details["image_path"])
        file_input.send_keys(absolute_image_path)
        
        print("Form on replica page filled successfully!")
        
        # Note: The time.sleep() here will still run, but you won't see the browser.
        # The script will just pause before quitting.
        time.sleep(5) 
        
        driver.quit()
        return True

    except Exception as e:
        print(f"ERROR in form_filler.py: {e}")
        if 'driver' in locals():
            driver.quit()
        return False
