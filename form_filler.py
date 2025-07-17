from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.utils import ChromeType  # <--- 1. DELETE THIS LINE

import time
import os

def submit_to_replica_form(user_details, complaint_details):
    """
    Automates filling our replica form for the 'chromium' package on Streamlit Cloud.
    """
    FORM_URL = "https://aesthetic-bunny-3b2ef2.netlify.app/"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    try:
        # --- 2. THIS IS THE CHANGE ---
        # Instead of using ChromeType, we pass the browser name as a string.
        service = Service(ChromeDriverManager(chrome_type='chromium').install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(FORM_URL)
        time.sleep(2)
        
        # ... (The rest of the file is IDENTICAL and CORRECT) ...
        
        driver.find_element(By.ID, "ContactNo").send_keys(user_details["phone"])
        driver.find_element(By.ID, "ComplainantName").send_keys(user_details["name"])
        driver.find_element(By.ID, "ComplaintLocation").send_keys("AI Generated Location Placeholder")
        driver.find_element(By.ID, "ComplaintComment").send_keys(complaint_details["description"])
        
        category_map = {"Damaged Road": "4", "Water Logging": "2", "Streetlight": "1"}
        select_element = Select(driver.find_element(By.ID, "ComplaintType"))
        value_to_select = category_map.get(complaint_details["category"], "4")
        select_element.select_by_value(value_to_select)
        
        file_input = driver.find_element(By.ID, "Image")
        absolute_image_path = os.path.abspath(complaint_details["image_path"])
        file_input.send_keys(absolute_image_path)
        
        print("Form on replica page filled successfully!")
        
        time.sleep(5) 
        
        driver.quit()
        return True

    except Exception as e:
        print(f"ERROR in form_filler.py: {e}")
        if 'driver' in locals():
            driver.quit()
        return False
