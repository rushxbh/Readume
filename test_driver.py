# Save this as test_driver.py and run it
import os
import sys

# Print environment info for debugging
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    # Import libraries
    print("Importing required libraries...")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("Libraries imported successfully")
    
    # Try creating the driver with minimal options first
    print("Creating Chrome driver with minimal options...")
    driver = webdriver.Chrome()
    print("Basic driver created successfully!")
    driver.quit()
    
    # Now try with your full options
    print("Creating Chrome driver with your options...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    print("Full options driver created successfully!")
    
    # Try accessing a site
    print("Accessing Google...")
    driver.get("https://www.google.com")
    print("Page loaded successfully!")
    
    driver.quit()
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    
    # Try to identify if the issue is with the Service or Options
    try:
        print("\nTrying alternative driver setup...")
        from selenium.webdriver.chrome.service import Service
        path_to_look = [".", "./chromedriver", "./chromedriver.exe", 
                        "/usr/local/bin/chromedriver", "C:/chromedriver.exe"]
        
        for path in path_to_look:
            if os.path.exists(path):
                print(f"Found potential driver at: {path}")
        
        print("If you see a path above, try using that explicitly.")
    except Exception as nested_e:
        print(f"Additional error during diagnosis: {nested_e}")