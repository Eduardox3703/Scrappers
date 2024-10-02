from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import concurrent.futures
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def wait_and_find_element(driver, by, value, timeout=20):  # Aumentado de 5 a 15 segundos
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def get_followers_from_countik(username):
    driver = setup_driver()
    try:
        countik_url = f"https://countik.com/user/@{username}"
        driver.get(countik_url)
        
        # Espera inicial para permitir que la página cargue completamente
        time.sleep(8)  # Aumentado de 0 a 8 segundos
        
        # Intentar obtener el elemento varias veces
        max_attempts = 3
        for attempt in range(max_attempts):
            followers_element = wait_and_find_element(driver, By.CSS_SELECTOR, 'h5.count')
            if followers_element and followers_element.text:
                followers_text = followers_element.text
                followers_count = ''.join(filter(str.isdigit, followers_text))
                if followers_count:
                    return followers_count
            time.sleep(3)  # Esperar 3 segundos entre intentos
        
        return "N/A"
    except Exception as e:
        print(f"Error al obtener seguidores para {username}: {e}")
        return "Error"
    finally:
        driver.quit()

def process_profile(username):
    print(f"Procesando @{username}...")
    followers_count = get_followers_from_countik(username)
    return {
        "Username": username,
        "Followers": followers_count,
        "Profile URL": f"https://www.tiktok.com/@{username}"
    }

def get_profile_info(usernames):
    profiles_data = []
    
    # Reducido el número de workers para evitar sobrecarga
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_username = {executor.submit(process_profile, username): username for username in usernames}
        
        for future in concurrent.futures.as_completed(future_to_username):
            try:
                profile_data = future.result()
                profiles_data.append(profile_data)
                print(f"Completado: @{profile_data['Username']} - Seguidores: {profile_data['Followers']}")
            except Exception as e:
                username = future_to_username[future]
                print(f"Error procesando {username}: {e}")
                profiles_data.append({
                    "Username": username,
                    "Followers": "Error",
                    "Profile URL": f"https://www.tiktok.com/@{username}"
                })
    
    return profiles_data

def save_to_csv(profiles_data, filename):
    if not profiles_data:
        print("No hay datos para guardar.")
        return
    
    fieldnames = ["Username", "Followers", "Profile URL"]
    
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(profiles_data)

def main():
    usernames = ['espinozapaz', 'matisse_mx', 'juansalazarjs', 'tierrablanca_angel', 'teoydiego', 
                 'canoaguilaroficial1', 'carolinarossmusic', 'christiannodal', 'jossfavela', 'angelaaguilar_',
                 'loshhoficial', 'talentolideroficial', 'manumedinaofficial', 'gaelcardona01', 'hugocoroneloficial',
                 'grupohistoriaofficial', 'latinpowermusic', 'katiaofficial', 'ivanciniflores', 'laejecutivaoficial',
                 'mprecordsmx', 'santosguzmanoficial', 'platasoficial', 'kevinmelendresoriginal', 'cristianjacobooficial',
                 'bandamachos_', 'eduincaz5', 'andreanunez_mx', 'banda_ms', 'javierlarranagaofficial', 'anabarbaraoficial',
                 'larrymania', 'ulisesronces', 'gallo_elizalde', 'grupofirme']
    
    filename = input('Nombra tu archivo .csv para guardar la información: ')
    
    print("Iniciando la extracción de datos...")
    start_time = time.time()
    
    profiles_data = get_profile_info(usernames)
    
    if profiles_data:
        save_to_csv(profiles_data, filename)
        print(f"Datos guardados en {filename}.csv")
        print(f"Se procesaron {len(profiles_data)} perfiles.")
    else:
        print("No se pudo obtener datos. Verifica la conexión o los nombres de usuario.")
    
    end_time = time.time()
    print(f"Tiempo total de ejecución: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()