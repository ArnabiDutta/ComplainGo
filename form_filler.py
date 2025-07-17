from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select # Needed for the dropdown
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def submit_to_replica_form(user_details, complaint_details):
    """
    Automates filling our replica of the PWD complaint form hosted on Netlify.
    
    Returns:
        bool: True if the process completes, False otherwise.
    """
    
    # --- Paste your live Netlify URL here ---
    FORM_URL = "https://aesthetic-bunny-3b2ef2.netlify.app/"
    
    # Set up the Selenium WebDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(FORM_URL)
        time.sleep(2) # Wait for the page to load
        
        # --- Fill the form using the element IDs from your HTML file ---
        
        # 1. Fill Text Inputs by their ID
        driver.find_element(By.ID, "ContactNo").send_keys(user_details["phone"])
        driver.find_element(By.ID, "ComplainantName").send_keys(user_details["name"])
        driver.find_element(By.ID, "ComplaintLocation").send_keys("AI Generated Location Placeholder") # A placeholder for the demo
        driver.find_element(By.ID, "ComplaintComment").send_keys(complaint_details["description"])
        
        # 2. Select from the Dropdown menu by its value
        # The values '4', '2', '1' match the <option value="..."> in your HTML
        # and the 'category' from your AI comes from labels.txt
        category_map = {"Damaged Road": "4", "Water Logging": "2", "Streetlight": "1"}
        select_element = Select(driver.find_element(By.ID, "ComplaintType"))
        
        # Find the correct value from our map based on the AI's prediction
        value_to_select = category_map.get(complaint_details["category"], "4") # Default to "Damaged Road" if not found
        select_element.select_by_value(value_to_select)
        
        # 3. Upload the Image by its ID
        file_input = driver.find_element(By.ID, "Image")
        absolute_image_path = os.path.abspath(complaint_details["image_path"])
        file_input.send_keys(absolute_image_path)
        
        print("Form on replica page filled successfully!")
        
        # Keep the filled form open for the audience to see for 15 seconds
        # before the browser automatically closes.
        time.sleep(15) 
        
        # You could optionally click the submit button for the demo
        driver.find_element(By.XPATH, '//button[text()="Submit"]').click()
        time.sleep(5) # Wait to see the alert
        
        driver.quit()
        return True

    except Exception as e:
        print(f"ERROR in form_filler.py: {e}")
        if 'driver' in locals():
            driver.quit()
        return False
