import requests
import lxml
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import random
import argparse
from tqdm import tqdm
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_sin_login.log"),
        logging.StreamHandler()
    ]
)

# Base URL para Forgotten Realms Wiki
FILE_URL_BASE = "https://forgottenrealms.fandom.com/wiki/"

# Crear directorio para guardar archivos si no existe
if not os.path.exists("Files"):
    os.makedirs("Files")
    logging.info("Directorio 'Files' creado para almacenar las imágenes")

# Función para descargar archivo sin necesidad de login
def download_file(driver, filename, retry_count=3):
    for attempt in range(retry_count):
        try:
            # Construir URL de la página del archivo
            url_string = FILE_URL_BASE + filename
            logging.debug(f"Navegando a {url_string}")
            driver.get(url_string)
            
            # Pequeña espera aleatoria para evitar bloqueos
            time.sleep(random.uniform(0.5, 2.0))
            
            # Obtener HTML de la página
            source = driver.page_source
            soup = bs4.BeautifulSoup(source, "lxml")
            
            # Buscar la URL de la imagen original usando meta tags
            url_tag = soup.find(property="og:image")
            if not url_tag:
                logging.warning(f"No se encontró la imagen para: {filename}")
                
                # Intentar encontrar la imagen usando otra estrategia
                img_div = soup.find('div', class_='fullImageLink')
                if img_div and img_div.find('a'):
                    url = img_div.find('a')['href']
                    logging.info(f"Encontrada imagen usando método alternativo: {url}")
                else:
                    return False
            else:
                url = url_tag["content"]
            
            # Descargar la imagen directamente sin necesidad de login
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            
            # Sanitizar el nombre del archivo
            safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
            output_path = os.path.join("Files", safe_filename[5:] if safe_filename.startswith("File:") else safe_filename)
            
            # Guardar la imagen en disco
            with open(output_path, "wb") as f:
                f.write(r.content)
            
            logging.info(f"Descargado: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error de red al descargar {filename}: {str(e)}")
        except Exception as e:
            logging.error(f"Error al descargar {filename}: {str(e)}")
        
        if attempt < retry_count - 1:
            wait_time = random.uniform(2, 5)
            logging.info(f"Reintentando en {wait_time:.2f} segundos...")
            time.sleep(wait_time)
        else:
            logging.error(f"Agotados los reintentos para: {filename}")
            return False

def process_files(filenames):
    # Configurar opciones del navegador para minimizar uso de recursos
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # Modo headless para no mostrar ventana
    
    # Iniciar WebDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)  # Establecer timeout para carga de páginas
        
        logging.info("WebDriver iniciado correctamente en modo headless")
        
        # Procesar archivos con barra de progreso
        total_files = len(filenames)
        success_count = 0
        failed_files = []
        
        for i, filename in enumerate(tqdm(filenames, desc="Descargando archivos")):
            # Comprobar si el archivo ya existe para no descargarlo de nuevo
            safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
            output_path = os.path.join("Files", safe_filename[5:] if safe_filename.startswith("File:") else safe_filename)
            
            if os.path.exists(output_path):
                logging.info(f"Archivo ya existe: {filename}")
                success_count += 1
                continue
                
            # Intentar descargar el archivo
            if download_file(driver, filename):
                success_count += 1
            else:
                failed_files.append(filename)
                
            # Pequeña pausa para evitar sobrecarga del servidor
            if i % 10 == 0 and i > 0:
                time.sleep(random.uniform(1, 3))
                
        # Resumen de resultados
        logging.info(f"Completado: {success_count}/{total_files} archivos descargados con éxito")
        
        # Guardar lista de archivos fallidos para reintentar más tarde
        if failed_files:
            failed_filename = "failed_files.txt"
            with open(failed_filename, "w", encoding="utf-8") as f:
                for failed in failed_files:
                    f.write(f"{failed}\n")
            logging.info(f"{len(failed_files)} archivos fallidos guardados en {failed_filename}")
            
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
    finally:
        driver.quit()
        logging.info("Proceso finalizado y navegador cerrado")

# Función principal
def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Descargador de imágenes de Forgotten Realms Wiki sin login")
    parser.add_argument("--failed", type=str, 
                        help="Archivo de lista de archivos fallidos para reintentar")
    args = parser.parse_args()
    
    # Cargar lista de archivos
    if args.failed:
        logging.info(f"Cargando archivos fallidos de {args.failed}")
        with open(args.failed, "r", encoding="utf-8") as f:
            filenames = f.read().splitlines()
    else:
        logging.info("Cargando lista completa de archivos...")
        with open("Filenames.txt", "r", encoding="utf-8") as f:
            filenames = f.read().splitlines()
    
    logging.info(f"Total de archivos a procesar: {len(filenames)}")
    
    # Procesar los archivos
    process_files(filenames)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Proceso interrumpido por el usuario.")
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")