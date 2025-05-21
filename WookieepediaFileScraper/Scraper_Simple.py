import requests
import lxml
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import random
import argparse
from tqdm import tqdm

# URL base para Forgotten Realms Wiki
FILE_URL_BASE = "https://forgottenrealms.fandom.com/wiki/"

# Crear directorio para guardar archivos si no existe
if not os.path.exists("Files"):
    os.makedirs("Files")

# Función para descargar un archivo
def download_file(driver, filename, retry_count=3):
    for attempt in range(retry_count):
        try:
            url_string = FILE_URL_BASE + filename                   # URL completa de la página del archivo
            driver.get(url_string)                                  # Navegar a la URL con Selenium
            
            # Pequeña espera aleatoria para evitar bloqueos
            time.sleep(random.uniform(1.0, 2.0))
            
            source = driver.page_source                             # Obtener HTML de la página
            soup = bs4.BeautifulSoup(source, "lxml")                # Parsear HTML con BeautifulSoup
            
            # Buscar la URL de la imagen original
            url_tag = soup.find(property="og:image")
            if not url_tag:
                print(f"No se encontró la imagen para: {filename}")
                return False
                
            url = url_tag["content"]                                # Obtener URL de la imagen original
            
            # Descargar la imagen
            r = requests.get(url, timeout=30)
            r.raise_for_status()  # Comprobar si la descarga fue exitosa
            
            # Sanitizar el nombre del archivo
            safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
            
            # Guardar la imagen en disco
            output_path = os.path.join("Files", safe_filename[5:])
            with open(output_path, "wb") as f:
                f.write(r.content)
            
            print(f"Descargado: {filename}")
            return True
            
        except Exception as e:
            print(f"Error al descargar {filename}: {str(e)}")
            if attempt < retry_count - 1:
                wait_time = random.uniform(2, 5)
                print(f"Reintentando en {wait_time:.2f} segundos...")
                time.sleep(wait_time)
            else:
                print(f"Agotados los reintentos para: {filename}")
                return False

def main():
    parser = argparse.ArgumentParser(description="Descargador simple de imágenes de Forgotten Realms Wiki")
    parser.add_argument("--failed", type=str, help="Archivo de lista de archivos fallidos para reintentar")
    parser.add_argument("--start", type=int, default=0, help="Índice de inicio para procesar archivos")
    parser.add_argument("--end", type=int, help="Índice final para procesar archivos")
    args = parser.parse_args()
    
    # Cargar lista de archivos
    if args.failed:
        print(f"Cargando archivos fallidos de {args.failed}")
        with open(args.failed, "r", encoding="utf-8") as f:
            filenames = f.read().splitlines()
    else:
        print("Cargando lista completa de archivos...")
        try:
            with open("Filenames.txt", "r", encoding="utf-8") as f:
                filenames = f.read().splitlines()
        except FileNotFoundError:
            print("Error: No se encontró el archivo 'Filenames.txt'")
            print("Por favor, ejecuta primero 'PopulateFilenameList.py' para generar la lista de archivos.")
            return
    
    # Ajustar rango de procesamiento
    start_idx = args.start
    end_idx = args.end if args.end is not None else len(filenames)
    
    # Validar índices
    if start_idx < 0 or start_idx >= len(filenames):
        print(f"Error: Índice de inicio ({start_idx}) fuera de rango.")
        return
    if end_idx <= start_idx or end_idx > len(filenames):
        print(f"Error: Índice final ({end_idx}) fuera de rango.")
        return
    
    # Calcular archivos a procesar
    files_to_process = filenames[start_idx:end_idx]
    print(f"Procesando {len(files_to_process)} archivos (desde {start_idx} hasta {end_idx-1})...")
    
    # Configurar opciones del navegador
    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Iniciar navegador
    driver = None
    try:
        print("Iniciando navegador Chrome...")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        
        # Iniciar sesión manualmente
        print("Navegando a la página de inicio de sesión de Fandom...")
        driver.get("https://www.fandom.com/signin")
        
        print("Por favor, inicia sesión manualmente en la ventana del navegador.")
        print("Una vez que hayas iniciado sesión, presiona 's' y Enter para continuar.")
        
        while True:
            resp = input("¿Has iniciado sesión? (s/n): ")
            if resp.lower() == 's':
                print("Continuando con la descarga...")
                break
            elif resp.lower() == 'n':
                print("Esperando 2 minutos más para que inicies sesión...")
                time.sleep(120)
            else:
                print("Respuesta no reconocida. Por favor, escribe 's' o 'n'.")
        
        # Procesar archivos con barra de progreso
        total_files = len(files_to_process)
        success_count = 0
        failed_files = []
        
        for i, filename in enumerate(tqdm(files_to_process, desc="Descargando archivos")):
            # Comprobar si el archivo ya existe para no descargarlo de nuevo
            safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
            output_path = os.path.join("Files", safe_filename[5:])
            
            if os.path.exists(output_path):
                print(f"Archivo ya existe: {filename}")
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
        print(f"Completado: {success_count}/{total_files} archivos descargados con éxito")
        
        # Guardar lista de archivos fallidos para reintentar más tarde
        if failed_files:
            failed_filename = "failed_files.txt"
            with open(failed_filename, "w", encoding="utf-8") as f:
                for failed in failed_files:
                    f.write(f"{failed}\n")
            print(f"{len(failed_files)} archivos fallidos guardados en {failed_filename}")
        
    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        if driver:
            driver.quit()
        print("Proceso finalizado")

if __name__ == "__main__":
    main()
