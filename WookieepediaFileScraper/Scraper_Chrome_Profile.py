import requests
import lxml
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import multiprocessing
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
                print(f"[Agente {multiprocessing.current_process().name}] No se encontró la imagen para: {filename}")
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
            
            print(f"[Agente {multiprocessing.current_process().name}] Descargado: {filename}")
            return True
            
        except Exception as e:
            print(f"[Agente {multiprocessing.current_process().name}] Error al descargar {filename}: {str(e)}")
            if attempt < retry_count - 1:
                wait_time = random.uniform(2, 5)
                print(f"[Agente {multiprocessing.current_process().name}] Reintentando en {wait_time:.2f} segundos...")
                time.sleep(wait_time)
            else:
                print(f"[Agente {multiprocessing.current_process().name}] Agotados los reintentos para: {filename}")
                return False

# Función para procesar un subconjunto de archivos con perfil de Chrome
def process_file_chunk(chunk_id, filenames_chunk, user_data_dir):
    driver = None  # Inicializar driver fuera del try para evitar UnboundLocalError
    
    try:
        print(f"[Agente {chunk_id+1}] Iniciando con perfil de Chrome: {user_data_dir}")
        
        # Configurar opciones del navegador con el perfil especificado
        options = Options()
        
        # Usar una carpeta temporal para el perfil para evitar conflictos
        temp_profile_dir = os.path.join(user_data_dir, f"TempProfile_{chunk_id}")
        if not os.path.exists(temp_profile_dir):
            os.makedirs(temp_profile_dir)
            
        options.add_argument(f"user-data-dir={temp_profile_dir}")
        
        # Estas opciones pueden ayudar a evitar problemas de inicio
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        
        # Estas opciones pueden ayudar si Chrome está crasheando
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Usar webdriver manager para descargar el driver automáticamente
        print(f"[Agente {chunk_id+1}] Iniciando Chrome...")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        
        # Verificar si ya hay una sesión activa
        print(f"[Agente {chunk_id+1}] Verificando sesión en Fandom...")
        driver.get("https://www.fandom.com/")
        time.sleep(5)
        
        # Verificar si necesitamos iniciar sesión (esto es solo una comprobación básica)
        from selenium.webdriver.common.by import By
        login_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'signin')]")
        if login_elements:
            print(f"[Agente {chunk_id+1}] Parece que necesitas iniciar sesión.")
            print(f"[Agente {chunk_id+1}] Navegando a la página de inicio de sesión...")
            driver.get("https://www.fandom.com/signin")
            
            # Dar tiempo al usuario para iniciar sesión manualmente
            print(f"[Agente {chunk_id+1}] Por favor, inicia sesión manualmente en la ventana del navegador.")
            print(f"[Agente {chunk_id+1}] Una vez que hayas iniciado sesión, presiona 's' y Enter para continuar.")
            
            while True:
                resp = input(f"[Agente {chunk_id+1}] ¿Has iniciado sesión? (s/n): ")
                if resp.lower() == 's':
                    print(f"[Agente {chunk_id+1}] Continuando con la descarga...")
                    break
                elif resp.lower() == 'n':
                    print(f"[Agente {chunk_id+1}] Esperando 2 minutos más para que inicies sesión...")
                    time.sleep(120)
                else:
                    print(f"[Agente {chunk_id+1}] Respuesta no reconocida. Por favor, escribe 's' o 'n'.")
        else:
            print(f"[Agente {chunk_id+1}] Sesión activa detectada. Continuando con la descarga...")
        
        # Procesar archivos con barra de progreso
        total_files = len(filenames_chunk)
        success_count = 0
        failed_files = []
        
        for i, filename in enumerate(tqdm(filenames_chunk, desc=f"Agente {chunk_id+1}", position=chunk_id)):
            # Comprobar si el archivo ya existe para no descargarlo de nuevo
            safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
            output_path = os.path.join("Files", safe_filename[5:])
            
            if os.path.exists(output_path):
                print(f"[Agente {chunk_id+1}] Archivo ya existe: {filename}")
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
        print(f"[Agente {chunk_id+1}] Completado: {success_count}/{total_files} archivos descargados con éxito")
          # Guardar lista de archivos fallidos para reintentar más tarde
        if failed_files:
            failed_filename = f"failed_files_agent{chunk_id+1}.txt"
            with open(failed_filename, "w", encoding="utf-8") as f:
                for failed in failed_files:
                    f.write(f"{failed}\n")
            print(f"[Agente {chunk_id+1}] {len(failed_files)} archivos fallidos guardados en {failed_filename}")
            
    except Exception as e:
        print(f"[Agente {chunk_id+1}] Error crítico: {str(e)}")
    finally:
        # Solo cerrar el driver si se inicializó correctamente
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                print(f"[Agente {chunk_id+1}] Error al cerrar el navegador: {str(e)}")
        print(f"[Agente {chunk_id+1}] Proceso finalizado")

# Dividir lista de archivos en chunks para procesamiento paralelo
def split_list(lst, n):
    """Divide una lista en n segmentos aproximadamente iguales"""
    chunk_size = len(lst) // n
    remainder = len(lst) % n
    result = []
    
    start = 0
    for i in range(n):
        # Añadir un elemento extra para los primeros 'remainder' chunks
        end = start + chunk_size + (1 if i < remainder else 0)
        result.append(lst[start:end])
        start = end
        
    return result

# Función principal
if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Descargador de imágenes de Forgotten Realms Wiki con perfil de Chrome")
    parser.add_argument("--agents", type=int, default=1, 
                        help="Número de agentes paralelos (default: 1)")
    parser.add_argument("--failed", type=str, 
                        help="Archivo de lista de archivos fallidos para reintentar")
    parser.add_argument("--profile", type=str, required=True,
                        help="Ruta al directorio de datos de usuario de Chrome (user-data-dir)")
    args = parser.parse_args()
    
    num_agents = args.agents
    user_data_dir = args.profile
      # Verificar que el directorio de perfil exista
    if not os.path.exists(user_data_dir):
        print(f"Error: El directorio de perfil de Chrome especificado no existe: {user_data_dir}")
        print("Por favor, proporciona una ruta válida al directorio de perfil de Chrome.")
        exit(1)
        
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
            exit(1)
    
    print(f"Total de archivos a procesar: {len(filenames)}")
    
    # Dividir los archivos en chunks para los agentes
    file_chunks = split_list(filenames, num_agents)
    
    print(f"Iniciando {num_agents} agentes en paralelo...")
    
    # Crear y ejecutar procesos
    processes = []
    for i in range(num_agents):
        print(f"Agente {i+1}: {len(file_chunks[i])} archivos asignados")
        p = multiprocessing.Process(
            target=process_file_chunk,
            args=(i, file_chunks[i], user_data_dir),
            name=f"Agente-{i+1}"
        )
        processes.append(p)
        p.start()
    
    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()
    
    print("¡Todos los agentes han completado su trabajo!")
    print("Comprueba los archivos de registro para ver los detalles de los archivos fallidos.")
