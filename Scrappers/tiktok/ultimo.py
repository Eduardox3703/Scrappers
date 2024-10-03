from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import time
import queue
import threading
import bt
import os

# Cola thread-safe para almacenar resultados
results_queue = queue.Queue()

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

def is_video(driver):
    try:
        video_element = driver.find_element(By.TAG_NAME, 'video')
        return True
    except NoSuchElementException:
        return False

def get_video_duration(driver):
    try:
        duration_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-1cuqcrm-DivSeekBarTimeContainer"))
        )
        duration_text = duration_element.text
        total_duration = duration_text.split('/')[-1].strip()
        return total_duration
    except Exception:
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

def process_video(video_link, index, total_videos):
    driver = setup_driver()
    try:
        print(f"Procesando video {index}/{total_videos}...")
        driver.get(video_link)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DivVideoInfoContainer")]'))
        )
        
        is_video_content = is_video(driver)
        video_duration = get_video_duration(driver) if is_video_content else "N/A"
        
        video_data = {
            "Número de Video": index,
            "URL del Video": video_link,
            "Es Video": is_video_content,
            "Duración": video_duration
        }
        
        try:
            title_container = wait_and_find_element(driver, By.XPATH, 
                '//div[contains(@class, "DivVideoInfoContainer")]')
            if title_container:
                regular_text = title_container.find_elements(By.XPATH, './/span[not(strong)]')
                strong_text = title_container.find_elements(By.XPATH, './/strong')
                
                full_title = ""
                
                for span in regular_text:
                    full_title += span.text + " "
                for strong in strong_text:
                    full_title += strong.text + " "
                
                video_data["Título"] = full_title.strip()
            else:
                video_data["Título"] = "N/A"
        except Exception as e:
            print(f"Error al extraer el título: {e}")
            video_data["Título"] = "N/A"
        
        elements_to_find = {
            "Likes": '//strong[@data-e2e="like-count"]',
            "Comentarios": '//strong[@data-e2e="comment-count"]',
            "Compartidos": '//strong[@data-e2e="share-count"]',
        }
        
        for key, xpath in elements_to_find.items():
            try:
                element = wait_and_find_element(driver, By.XPATH, xpath)
                video_data[key] = element.text if element else "N/A"
            except Exception:
                video_data[key] = "N/A"
        
        results_queue.put(video_data)
        return True
    except Exception as e:
        print(f"Error al procesar el video {index}: {e}")
        return False
    finally:
        driver.quit()

def get_videos_info(target_profile, max_workers=4):
    main_driver = setup_driver()
    website = f"https://www.tiktok.com/@{target_profile}"
    main_driver.get(website)
    
    print("Si aparece un CAPTCHA, resuélvelo manualmente.")
    input("Presiona Enter una vez que la página haya cargado completamente...")

    try:
        print("Cargando todos los videos...")
        scroll_to_load_all_videos(main_driver)
        
        video_links = [element.get_attribute('href') for element in 
                       main_driver.find_elements(By.XPATH, '//div[@data-e2e="user-post-item"]//a')]
        total_videos = len(video_links)
        print(f"Total de videos encontrados: {total_videos}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_video, link, i+1, total_videos) 
                      for i, link in enumerate(video_links)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error en thread: {e}")

    except Exception as e:
        print(f"Error general: {e}")
    finally:
        main_driver.quit()
    
    videos_data = []
    while not results_queue.empty():
        videos_data.append(results_queue.get())
    
    videos_data.sort(key=lambda x: x["Número de Video"])
    return videos_data

def save_to_csv(videos_data, filename):
    if not videos_data:
        print("No hay datos para guardar.")
        return
    
    fieldnames = ["Número de Video", "Es Video", "Título", "Duración", "Likes", 
                  "Comentarios", "Compartidos", "URL del Video"]
    
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(videos_data)

if __name__ == "__main__":
    target_profile = input('Introduce la cuenta de TikTok a la que quieres acceder: ')
    filename = input('Nombra tu archivo .csv para la información de los videos: ')
    num_workers = int(input('Introduce el número de workers para el procesamiento paralelo (recomendado 4-8): '))
    
    print("Iniciando la extracción de datos...")
    videos_data = get_videos_info(target_profile, max_workers=num_workers)
    
    if videos_data:
        save_to_csv(videos_data, filename)
        print(f"Datos de los videos guardados en {filename}.csv")
        print(f"Se procesaron exitosamente {len(videos_data)} videos.")
    else:
        print("No se pudo obtener datos. Verifica la conexión o el nombre de usuario.")

    #bt.main()