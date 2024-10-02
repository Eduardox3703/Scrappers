from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import os
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

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_comments_section(driver, comments_dir):
    try:
        comments_section = wait_and_find_element(driver, By.XPATH, 
            '//div[contains(@class, "DivCommentListContainer")] | //div[contains(@class, "comment-list")] | //div[contains(@data-e2e, "comment-list")]')
        
        if comments_section:
            # Scroll para cargar más comentarios
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(10):  # Reducido a 5 scrolls para optimizar tiempo
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Reducido el tiempo de espera
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            comments_html = comments_section.get_attribute('outerHTML')
            file_path = os.path.join(comments_dir, 'latest_video_comments.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(comments_html)
            return True
    except Exception as e:
        print(f"Error al guardar la sección de comentarios: {e}")
    return False

def get_videos_info(target_profile, comments_dir):
    driver = setup_driver()
    website = f"https://www.tiktok.com/@{target_profile}"
    driver.get(website)
    
    print("Si aparece un CAPTCHA, resuélvelo manualmente.")
    input("Presiona Enter una vez que la página haya cargado completamente...")

    create_directory(comments_dir)
    videos_data = []
    first_video_processed = False

    try:
        posts = driver.find_elements(By.XPATH, '//div[@data-e2e="user-post-item"]')
        
        for index, post in enumerate(posts[:10], 1):
            try:
                print(f"Procesando video {index}/10...")
                video_link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                # Abrir video en nueva pestaña
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(video_link)
                
                # Esperar a que cargue el título (indicador de que la página está lista)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "DivVideoInfoContainer")]'))
                )
                
                # Extraer información del video eficientemente
                video_data = {
                    "Número de Video": index,
                    "URL del Video": video_link
                }
                
                # Buscar elementos y asignar valores
                elements_to_find = {
                    "Título": '//div[contains(@class, "DivVideoInfoContainer")]//span',
                    "Likes": '//strong[@data-e2e="like-count"]',
                    "Comentarios": '//strong[@data-e2e="comment-count"]',
                    "Compartidos": '//strong[@data-e2e="share-count"]'
                }
                
                for key, xpath in elements_to_find.items():
                    element = wait_and_find_element(driver, By.XPATH, xpath)
                    video_data[key] = element.text if element else "N/A"
                
                # Para el primer video, guardar la sección de comentarios
                if not first_video_processed:
                    print("Guardando comentarios del primer video...")
                    comments_saved = save_comments_section(driver, comments_dir)
                    video_data["Comentarios Guardados"] = "Sí" if comments_saved else "No"
                    first_video_processed = True
                
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
    
    fieldnames = ["Número de Video", "Título", "Likes", "Comentarios", "Compartidos", 
                  "Comentarios Guardados", "URL del Video"]
    
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(videos_data)

if __name__ == "__main__":
    target_profile = input('Introduce la cuenta de TikTok a la que quieres acceder: ')
    filename = input('Nombra tu archivo .csv para la información de los videos: ')
    comments_dir = input('Introduce el nombre del directorio para guardar los comentarios: ')
    
    print("Iniciando la extracción de datos...")
    videos_data = get_videos_info(target_profile, comments_dir)
    
    if videos_data:
        save_to_csv(videos_data, filename)
        print(f"Datos de los videos guardados en {filename}.csv")
        print(f"Se procesaron exitosamente {len(videos_data)} videos.")
        print(f"Comentarios del primer video guardados en {comments_dir}/latest_video_comments.html")
    else:
        print("No se pudo obtener datos. Verifica la conexión o el nombre de usuario.")


    bt.main()