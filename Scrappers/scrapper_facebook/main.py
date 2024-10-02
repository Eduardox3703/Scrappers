from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import csv
import time

# Credenciales de usuario (asegúrate de que sean válidas y estén protegidas)
username = 'dudedeveloper08@gmail.com'
password = 'Este es el correo del dude developer 89'
prefix = 'https://www.facebook.com/'
texts = []
images = []

# Función de desplazamiento
def scroll():
    scroll_origin = ScrollOrigin.from_viewport(10, 10)
    ActionChains(driver)\
        .scroll_from_origin(scroll_origin, 0, 10000)\
        .perform()

# Crear el controlador web para realizar una solicitud GET a la página de Facebook
website = prefix + input('Introduce la URL del sitio a hacer scraping: ')
name = input('Nombra tu archivo CSV: ')

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)
driver.get(website)

# Hacemos que el controlador espere hasta que todos los elementos estén en pantalla
driver.implicitly_wait(60)  # espera 60 segundos o hasta que se encuentre todo

# Proceso de inicio de sesión
try:
    email = driver.find_element(By.XPATH, '//input[@type="text"]').send_keys(username)
    pw = driver.find_element(By.XPATH, '//label[@aria-label="Contraseña"]/input').send_keys(password)
    time.sleep(5)
    login = driver.find_element(By.XPATH, '//div[@class="x1n2onr6 x1ja2u2z x78zum5 x2lah0s xl56j7k x6s0dn4 xozqiw3 x1q0g3np xi112ho x17zwfj4 x585lrc x1403ito x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xn6708d x1ye3gou xtvsq51 x1fq8qgq"]')
    login.click()
except Exception as e:
    print(f"Inicio de sesión fallido: {e}")

# Haciendo scraping de las publicaciones en el timeline
try:
    timeline = driver.find_elements(By.XPATH, '//div[@data-pagelet="ProfileTimeline"]')
    time.sleep(10)
    for element in timeline:
        print(element.text)
except Exception as e:
    print(f"Error al hacer scraping del timeline: {e}")

# Guardando en CSV (si el scraping fue exitoso)
try:
    with open(f'{name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Título', 'Likes', 'Comentarios', 'Shares']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()    

        # Ejemplo de placeholder para las filas de datos (asumiendo que se ha recopilado correctamente)
        for data in zip(titles, reactions, comments, shares):
            writer.writerow({"Título": data[0], "Likes": data[1], "Comentarios": data[2], "Shares": data[3]})
except Exception as e:
    print(f"Error al escribir en el CSV: {e}")

driver.quit()
