from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login(driver, username, password):
    try:
        driver.get("https://www.instagram.com/")
        time.sleep(5)

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Inicio']"))
        )

        print("Inicio de sesión exitoso")
        return True
    except Exception as e:
        print(f"Error durante el inicio de sesión: {e}")
        return False

def get_user_info(driver, target_profile):
    try:
        profile_url = f"https://www.instagram.com/{target_profile}/"
        driver.get(profile_url)
        time.sleep(5)

        # Get username
        username_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft"))
        )
        username = username_element.text

        # Get number of posts
        post_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.html-span.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1hl2dhg.x16tdsg8.x1vvkbs"))
        )
        post_count = post_count_element.text

        # Get user link
        user_link = profile_url

        return username, post_count, user_link
    except Exception as e:
        print(f"Error al obtener la información del usuario: {e}")
        return None, None, None

def main():
    target_profile = "carinleonoficial"
    username = "rbrtmtz43"
    password = "qwerty12345"

    driver = setup_driver()
    try:
        if login(driver, username, password):
            username, post_count, user_link = get_user_info(driver, target_profile)
            if username and post_count and user_link:
                print(f"Username: {username}")
                print(f"Número de posts: {post_count}")
                print(f"Link del usuario: {user_link}")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()