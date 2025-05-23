import requests
import lxml
import bs4
import os
import time
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Desactivar advertencias SSL para requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FILE_URL_BASE = "https://forgottenrealms.fandom.com/wiki/"

USERNAME = "USER"
PASSWORD = "PASSWORD"

# Ensure the Files directory exists
os.makedirs("Files", exist_ok=True)

filenames = []

# Log in to your Fandom account.
def auto_login(d, username, password):
    print("Iniciando proceso de login en Fandom...")
    
    try:
        # Usando URL alternativa que podría ser más estable
        d.get("https://community.fandom.com/signin")
        
        # Esperamos a que la página cargue completamente
        time.sleep(5)
        print("Página de inicio de sesión cargada...")
        
        # Intentar detectar si ya iniciamos sesión
        try:
            # Buscar algún elemento que indique que estamos conectados
            avatar = d.find_element(By.CSS_SELECTOR, ".wds-avatar")
            print("Ya has iniciado sesión en Fandom. Continuando...")
            return
        except NoSuchElementException:
            print("No se ha detectado sesión activa, procediendo con el login...")
        
        try:
            # Esperar explícitamente por elementos de login
            wait = WebDriverWait(d, 10)
            
            # Diferentes selectores que podríamos probar
            selectors = [
                {"by": By.CSS_SELECTOR, "value": "input[name='username']"},
                {"by": By.ID, "value": "username"},
                {"by": By.CSS_SELECTOR, "value": ".wds-input__field"}
            ]
            
            uname = None
            for selector in selectors:
                try:
                    print(f"Intentando selector {selector['value']}...")
                    uname = wait.until(EC.presence_of_element_located((selector["by"], selector["value"])))
                    break
                except:
                    continue
                    
            if uname is not None:
                print("Campo de usuario encontrado")
                uname.clear()
                uname.send_keys(username)
                
                # Buscar campo de contraseña
                try:
                    pswrd = None
                    # Intentar encontrar el campo de contraseña
                    try:
                        pswrd = d.find_element(By.CSS_SELECTOR, "input[name='password']")
                    except:
                        try:
                            pswrd = d.find_element(By.ID, "password")
                        except:
                            # Última opción: buscar todos los inputs y agarrar el segundo
                            inputs = d.find_elements(By.CSS_SELECTOR, "input[type='password']")
                            if inputs and len(inputs) > 0:
                                pswrd = inputs[0]
                    
                    if pswrd:
                        pswrd.clear()
                        pswrd.send_keys(password)
                        
                        # Intentar encontrar el botón de submit
                        try:
                            login_button = d.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        except:
                            # Buscar cualquier botón que pueda servir para login
                            login_button = d.find_element(By.CSS_SELECTOR, "button.submit")
                        
                        if login_button:
                            login_button.click()
                            print("Formulario de inicio de sesión enviado")
                            
                            # Esperar a que el usuario complete el CAPTCHA si es necesario
                            x = input("Completar CAPTCHA si es necesario y presionar Enter cuando esté listo...")
                            print("¡Inicio de sesión completado!")
                            return
                except Exception as e:
                    print(f"Error al intentar hacer login con formulario: {e}")
        except Exception as e:
            print(f"Error intentando usar el formulario: {e}")
        
        print("No se pudo realizar el inicio de sesión automático.")
                
    except Exception as e:
        print(f"Error general durante el inicio de sesión: {e}")
    
    # Si llegamos aquí, ninguno de los métodos funcionó
    print("Por favor, inicia sesión manualmente:")
    print(f"1. URL actual: {d.current_url}")
    print("2. Usa el navegador que se ha abierto para iniciar sesión")
    x = input("3. Presiona Enter cuando hayas terminado...(espera a que la página termine de cargar)")
    time.sleep(2)  # Dar tiempo para que termine cualquier redirección
    print("Continuando con el script...")

# Download the image at the given filename
def download_file(filename):
    try:
        url_string = FILE_URL_BASE + filename                   # This is the full url of the file page on the wiki
        driver.get(url_string)                                  # Send Selenium to that URL
        source = driver.page_source                             # Read the page's HTML
        soup = bs4.BeautifulSoup(source, "lxml")                # Parse the HTML with BeautifulSoup
        
        # Buscar la imagen y manejar el caso en que no se encuentre
        img_tag = soup.find(property="og:image")
        if img_tag is None:
            print(f"No se encontró la imagen para {filename}. Saltando...")
            return
            
        url = img_tag["content"]                               # Get the URL of the original file in the wiki database
        r = requests.get(url, verify=False)                     # Get the image with SSL verification disabled
        print(filename)
        filename = filename.replace('"', '_')                   # Replace characters that can't be in the filename
        filename = filename.replace('?', '_')
        with open("Files/" + filename[5:], "wb") as f:          # Write the image to a file with the same filename
            f.write(r.content)
    except Exception as e:
        print(f"Error al descargar {filename}: {e}")
        print("Continuando con el siguiente archivo...")

# Identify the files we want to download
with open("Filenames.txt", "r", encoding="utf-8") as f:
    filenames = f.read().splitlines()
f.close()

# Configure Chrome options
chrome_options = Options()
# Uncomment the following line if you want to run Chrome in headless mode
# chrome_options.add_argument("--headless")

# Configuraciones adicionales para evitar problemas de SSL y mejora de rendimiento
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")

# Setup Chrome WebDriver - Selenium 4 way
# En Selenium 4, se recomienda usar el objeto Options directamente
driver = webdriver.Chrome(options=chrome_options)
auto_login(driver, USERNAME, PASSWORD)

for item in filenames:
    download_file(item)
