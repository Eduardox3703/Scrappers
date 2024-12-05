from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import bt

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def wait_and_find_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def get_video_duration(driver):
    try:
        # Esperar y encontrar el elemento de duración usando la clase específica
        duration_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-1cuqcrm-DivSeekBarTimeContainer"))
        )
        
        # El texto será algo como "00:01 / 00:16"
        duration_text = duration_element.text
        
        # Extraer la duración total (la parte después del '/')
        total_duration = duration_text.split('/')[-1].strip()
        
        return total_duration
    except Exception as e:
        print(f"Error al obtener la duración: {e}")
        return "N/A"

def scroll_to_load_all_videos(driver):
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
        posts = driver.find_elements(By.XPATH, '//div[@data-e2e="user-post-item"]')
        print(f"Videos cargados: {len(posts)}")

def get_videos_info(target_profile):
    driver = setup_driver()
    website = f"https://www.tiktok.com/@{target_profile}"
    driver.get(website)
    
    print("Si aparece un CAPTCHA, resuélvelo manualmente.")
    input("Presiona Enter una vez que la página haya cargado completamente...")

    videos_data = []

    try:
        print("Cargando todos los videos...")
        scroll_to_load_all_videos(driver)
        
        posts = driver.find_elements(By.XPATH, '//div[@data-e2e="user-post-item"]')
        total_videos = len(posts)
        print(f"Total de videos encontrados: {total_videos}")

        for index, post in enumerate(posts, 1):
            try:
                print(f"Procesando video {index}/{total_videos}...")
                video_link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                # Abrir video en nueva pestaña
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(video_link)
                
                # Esperar a que cargue la información del video
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DivVideoInfoContainer")]'))
                )
                
                # Obtener la duración del video usando la nueva función
                video_duration = get_video_duration(driver)
                
                video_data = {
                    "Número de Video": index,
                    "URL del Video": video_link,
                    "Duración": video_duration
                }
                
                # Elementos a buscar y extraer
                elements_to_find = {
                    "Título": '//div[contains(@class, "DivVideoInfoContainer")]//span',
                    "Likes": '//strong[@data-e2e="like-count"]',
                    "Comentarios": '//strong[@data-e2e="comment-count"]',
                    "Compartidos": '//strong[@data-e2e="share-count"]',
                    ##"Música": '//h4[contains(@class, "music-title-link")]',
                    "Descripción": '//div[contains(@class, "DivVideoDescContainer")]',
                    "Hashtags": '//a[contains(@class, "video-tag")]',
                    "Fecha de Publicación": '//span[contains(@class, "DivTimeTag")]'
                }
                
                for key, xpath in elements_to_find.items():
                    try:
                        if key == "Hashtags":
                            elements = driver.find_elements(By.XPATH, xpath)
                            video_data[key] = ", ".join([el.text for el in elements]) if elements else "N/A"
                        else:
                            element = wait_and_find_element(driver, By.XPATH, xpath)
                            video_data[key] = element.text if element else "N/A"
                    except Exception as e:
                        video_data[key] = "N/A"
                        print(f"Error al obtener {key}: {str(e)}")
                
                videos_data.append(video_data)
                
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print(f"Error al procesar el video {index}: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Error general: {e}")
    finally:
        driver.quit()
    
    return videos_data

def save_to_csv(videos_data, filename):
    if not videos_data:
        print("No hay datos para guardar.")
        return
    
    fieldnames = ["Número de Video", "Título", "Duración", "Likes", "Comentarios", 
                  "Compartidos", "Música", "Descripción", "Hashtags", 
                  "Fecha de Publicación", "URL del Video"]
    
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(videos_data)

if __name__ == "__main__":
    target_profile = input('Introduce la cuenta de TikTok a la que quieres acceder: ')
    filename = input('Nombra tu archivo .csv para la información de los videos: ')
    
    print("Iniciando la extracción de datos...")
    videos_data = get_videos_info(target_profile)
    
    if videos_data:
        save_to_csv(videos_data, filename)
        print(f"Datos de los videos guardados en {filename}.csv")
        print(f"Se procesaron exitosamente {len(videos_data)} videos.")
    else:
        print("No se pudo obtener datos. Verifica la conexión o el nombre de usuario.")

    bt.main()