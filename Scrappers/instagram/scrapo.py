from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import platform
import os

class InstagramScraper:
    def __init__(self):
        chrome_options = Options()
        # Uncomment for headless mode if needed
        # chrome_options.add_argument("--headless=new")  # Updated headless argument
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Additional options for stability
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            service = Service()  # Let Selenium find the appropriate driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            print(f"Error initializing driver: {str(e)}")
            raise

    def navigate_to_url(self, url):
        try:
            print(f"Navigating to URL: {url}")
            self.driver.get(url)
            time.sleep(2)  # Give the page some time to load
        except WebDriverException as e:
            print(f"Error loading URL: {str(e)}")
            return False
        return True

    def get_follower_count(self, username):
        if not self.navigate_to_url(f"https://www.instagram.com/{username}/"):
            return "Error loading URL"
        
        try:
            # Wait for the followers count to be visible
            followers_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li:nth-child(2) span span"))
            )
            follower_count = followers_element.text
            print(f"Follower count found: {follower_count}")
            return follower_count
        except Exception as e:
            print(f"Error getting follower count: {str(e)}")
            return "Not available"
    
    def close(self):
        try:
            self.driver.quit()
        except:
            pass

def main():
    try:
        scraper = InstagramScraper()
        username = "carinleonoficial"
        print(f"Getting follower count for {username}... this may take a few seconds.")
        
        follower_count = scraper.get_follower_count(username)
        
        if follower_count and follower_count != "Not available":
            print(f"Followers: {follower_count}")
        else:
            print("Error getting follower count.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()