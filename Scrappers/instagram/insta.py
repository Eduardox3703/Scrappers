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

def get_post_count(driver, target_profile):
    try:
        driver.get(f"https://www.instagram.com/{target_profile}/")
        time.sleep(5)

        # Buscar el elemento que contiene el número de publicaciones
        meta_section = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span._ac2a"))
        )
        
        # El primer elemento suele ser el número de publicaciones
        post_count = meta_section[0].text
        
        print(f"El perfil {target_profile} tiene {post_count} publicaciones")
        return post_count
    except Exception as e:
        print(f"Error al obtener el número de publicaciones: {e}")
        return None

def main():
    target_profile = "carinleonoficial"
    username = "rbrtmtz43"
    password = "qwerty12345"

    driver = setup_driver()
    try:
        if login(driver, username, password):
            post_count = get_post_count(driver, target_profile)
            if post_count:
                print(f"Número total de publicaciones encontradas: {post_count}")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()