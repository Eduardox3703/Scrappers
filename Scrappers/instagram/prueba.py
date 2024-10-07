from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import time
import queue
import threading
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

def login(driver, username, password):
    try:
        driver.get("https://www.instagram.com/")
        time.sleep(5)  # Esperar a que la página cargue

        if "accounts/login" not in driver.current_url:
            try:
                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Entrar')]"))
                )
                login_button.click()
                time.sleep(3)
            except:
                print("No se encontró el botón de inicio de sesión, asumiendo que ya estamos en la página de login")

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='_aagx']"))
        )

        print("Inicio de sesión exitoso")
    except Exception as e:
        print(f"Error durante el inicio de sesión: {e}")
        raise

def scroll_to_load_all_posts(driver, max_posts=None):
    SCROLL_PAUSE_TIME = 2
    posts_loaded = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Mostrar más publicaciones')]"))
            )
            driver.execute_script("arguments[0].click();", load_more_button)
            print("Clicked 'Mostrar más publicaciones' button")
            time.sleep(SCROLL_PAUSE_TIME)
        except (TimeoutException, ElementClickInterceptedException):
            print("No 'Mostrar más publicaciones' button found or not clickable")
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        posts = driver.find_elements(By.XPATH, '//article')
        posts_loaded = len(posts)
        print(f"Posts cargados: {posts_loaded}")
        
        if max_posts and posts_loaded >= max_posts:
            print(f"Se alcanzó el número máximo de posts ({max_posts})")
            break
        
        if new_height == last_height:
            print("No se pueden cargar más posts")
            break
        last_height = new_height

def is_video(driver):
    try:
        video_element = driver.find_element(By.TAG_NAME, 'video')
        return True
    except NoSuchElementException:
        return False

def process_post(post_link, index, total_posts):
    driver = setup_driver()
    try:
        print(f"Procesando post {index}/{total_posts}...")
        driver.get(post_link)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//article'))
        )
        
        is_video_content = is_video(driver)
        
        post_data = {
            "Número de Post": index,
            "URL del Post": post_link,
            "Es Video": is_video_content,
        }
        
        try:
            caption_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_a9zs")]'))
            )
            post_data["Descripción"] = caption_element.text if caption_element else "N/A"
        except Exception as e:
            print(f"Error al extraer la descripción: {e}")
            post_data["Descripción"] = "N/A"
        
        elements_to_find = {
            "Likes": '//section//span//span[contains(@class, "_aacl")]',
            "Comentarios": '//span[contains(@class, "_aacl") and contains(text(), "comments")]',
        }
        
        for key, xpath in elements_to_find.items():
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                post_data[key] = element.text if element else "N/A"
            except Exception:
                post_data[key] = "N/A"
        
        results_queue.put(post_data)
        return True
    except Exception as e:
        print(f"Error al procesar el post {index}: {e}")
        return False
    finally:
        driver.quit()

def click_search_icon(driver):
    try:
        # Esperar a que el enlace esté presente y sea clickeable
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='_a6hd']"))
        )
        search_icon.click()
        print("Se hizo clic en el ícono de búsqueda")
    except Exception as e:
        print(f"Error al hacer clic en el ícono de búsqueda: {e}")

def get_posts_info(target_profile, username, password, max_workers=4, max_posts=None):
    main_driver = setup_driver()
    try:
        login(main_driver, username, password)
        website = f"https://www.instagram.com/{target_profile}/"
        main_driver.get(website)
        time.sleep(5)  # Esperar a que la página cargue después del inicio de sesión
        
        # Clic en el ícono de búsqueda
        click_search_icon(main_driver)

        print("Cargando posts...")
        scroll_to_load_all_posts(main_driver, max_posts)
        
        post_links = [element.get_attribute('href') for element in 
                      main_driver.find_elements(By.XPATH, '//article//a[contains(@href, "/p/")]')]
        total_posts = len(post_links)
        print(f"Total de posts encontrados: {total_posts}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_post, link, i+1, total_posts) 
                      for i, link in enumerate(post_links[:max_posts] if max_posts else post_links)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error en thread: {e}")

    except Exception as e:
        print(f"Error general: {e}")
    finally:
        main_driver.quit()
    
    posts_data = []
    while not results_queue.empty():
        posts_data.append(results_queue.get())
    
    posts_data.sort(key=lambda x: x["Número de Post"])
    return posts_data

def save_to_csv(posts_data, filename):
    if not posts_data:
        print("No hay datos para guardar.")
        return
    
    fieldnames = ["Número de Post", "Es Video", "Descripción", "Likes", 
                  "Comentarios", "URL del Post"]
    
    with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts_data)

if __name__ == "__main__":
    target_profile = "carinleonoficial"
    username =  "rbrtmtz43"
    password = "qwerty12345"
    filename = "po"
    num_workers = 4
    max_posts = 0
    
    print("Iniciando la extracción de datos...")
    posts_data = get_posts_info(target_profile, username, password, max_workers=num_workers, max_posts=max_posts if max_posts > 0 else None)
    
    if posts_data:
        save_to_csv(posts_data, filename)
        print(f"Datos de los posts guardados en {filename}.csv")
        print(f"Se procesaron exitosamente {len(posts_data)} posts.")
    else:
        print("No se encontraron posts.")
