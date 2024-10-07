import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_instagram_followers(username, chrome_binary_path=None):
    chrome_options = Options()
    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path
    
    # Agregar opciones para evitar la detección de automatización
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Modificar el user-agent
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        
    except Exception as e:
        print(f"Error al inicializar el driver de Chrome: {e}")
        print("Asegúrate de que Chrome esté instalado en tu sistema.")
        print("Si Chrome está instalado en una ubicación no estándar, proporciona la ruta al binario.")
        return None

    try:
        driver.get("https://twicsy.com/instagram-follower-counter")
        
        # Esperar a que la página se cargue completamente
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        
        input_field = driver.find_element(By.XPATH, "//input[@name='username']")
        input_field.send_keys(username)
        input_field.send_keys(Keys.RETURN)
    
        # Aumentar el tiempo de espera y usar una espera explícita
        follower_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='profile-followers']/span[@class='val']"))
        )

        # Esperar un poco más para asegurarse de que el contenido se haya cargado
        time.sleep(2)

        follower_count = follower_element.text.replace(".", "")  # Eliminar puntos del número
        return follower_count

    except Exception as e:
        print(f"Error al obtener el número de seguidores: {e}")
        return None

    finally:
        driver.quit()

def save_to_csv(data, filename="followers_data.csv"):
    header = ["Username", "Followers"]
    try:
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            file.seek(0, 2)
            if file.tell() == 0:
                writer.writerow(header)  # Escribir encabezado si el archivo está vacío
            writer.writerow(data)
        print(f"Datos guardados en {filename}")
    except Exception as e:
        print(f"Error al guardar en el archivo CSV: {e}")

if __name__ == "__main__":
    username = input("Ingresar el Nombre de Usuario a buscar")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        followers = get_instagram_followers(username)
        if followers:
            print(f"El número de seguidores de {username} es: {followers}")
            save_to_csv([username, followers])
            break
        else:
            print(f"Intento {attempt + 1} fallido. Reintentando...")
            time.sleep(5)  # Esperar 5 segundos antes de reintentar
    else:
        print("No se pudo obtener el número de seguidores después de varios intentos.")
