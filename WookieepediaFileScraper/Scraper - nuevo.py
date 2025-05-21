import requests
import lxml
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import multiprocessing
import random
import argparse
from tqdm import tqdm

# Cambiado a Forgotten Realms según el contexto del archivo
FILE_URL_BASE = "https://forgottenrealms.fandom.com/wiki/"

USERNAME = "kroryan"
PASSWORD = "Adrian010397@"

# Crear directorio para guardar archivos si no existe
if not os.path.exists("Files"):
    os.makedirs("Files")

filenames = []

# Log in to your Fandom account (manual login).
def auto_login(d, username, password):
    try:
        from selenium.webdriver.common.by import By
        
        # Ir a la página de inicio y esperar a que cargue completamente
        print(f"[Agente {multiprocessing.current_process().name}] Navegando a la página de inicio de sesión...")
        d.get("https://www.fandom.com/signin")
        
        # Imprimir instrucciones para el usuario
        print(f"[Agente {multiprocessing.current_process().name}] Por favor, inicia sesión manualmente en la ventana del navegador.")
        print(f"[Agente {multiprocessing.current_process().name}] Tienes 10 minutos para iniciar sesión manualmente.")
        print(f"[Agente {multiprocessing.current_process().name}] Cuando hayas terminado, presiona 's' y Enter para continuar.")
        
        # Esperar a que el usuario inicie sesión manualmente
        time.sleep(10)  # Dar tiempo para que la página cargue
        
        # Preguntar al usuario si completó el inicio de sesión
        resp = input("¿Has iniciado sesión manualmente? (s/n): ")
        if resp.lower() == 's':
            print(f"[Agente {multiprocessing.current_process().name}] Inicio de sesión manual confirmado.")
            return True
        
        print(f"[Agente {multiprocessing.current_process().name}] Inicio de sesión cancelado.")
        return False
        
    except Exception as e:
        print(f"[Agente {multiprocessing.current_process().name}] Error en inicio de sesión: {str(e)}")
        
        # Preguntar si desea continuar manualmente
        resp = input("¿Has iniciado sesión manualmente a pesar del error? (s/n): ")
        if resp.lower() == 's':
            return True
        return False

# Download the image at the given filename
def download_file(driver, filename, retry_count=3):
    for attempt in range(retry_count):
        try:
            url_string = FILE_URL_BASE + filename                   # URL completa de la página del archivo
            driver.get(url_string)                                  # Navegar a la URL con Selenium
            
            # Pequeña espera aleatoria para evitar bloqueos
            time.sleep(random.uniform(0.5, 2.0))
            
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

# Función para procesar un subconjunto de archivos
def process_file_chunk(chunk_id, filenames_chunk):
    # Configurar opciones del navegador para minimizar uso de recursos
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # Evitar que los navegadores se cierren automáticamente después de cualquier error
    options.add_experimental_option("detach", True)
    
    # Iniciar WebDriver con WebDriverManager (automático)
    try:
        # Este método descargará automáticamente el driver correcto para tu versión de Chrome
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)  # Establecer timeout para carga de páginas
        driver.maximize_window()  # Maximizar ventana para mejor visualización
        
        print(f"[Agente {chunk_id+1}] Iniciando proceso de inicio de sesión manual...")
        
        # Intentar inicio de sesión manual directamente
        login_success = False
        max_attempts = 2  # Máximo 2 intentos de inicio de sesión manual
        
        for attempt in range(max_attempts):
            print(f"[Agente {chunk_id+1}] Intento de inicio de sesión manual #{attempt+1}")
            driver.get("https://www.fandom.com/signin")
            
            print(f"[Agente {chunk_id+1}] Por favor, inicia sesión manualmente en la ventana del navegador.")
            print(f"[Agente {chunk_id+1}] Tienes 10 minutos para iniciar sesión manualmente.")
            
            # Esperar a que el usuario complete el inicio de sesión
            time.sleep(60)  # Dar un minuto inicial
            
            # Preguntar cada minuto si el usuario ha completado el inicio de sesión
            for i in range(9):  # 9 minutos adicionales
                resp = input(f"[Agente {chunk_id+1}] ¿Has completado el inicio de sesión? (s/n): ")
                if resp.lower() == 's':
                    login_success = True
                    break
                print(f"[Agente {chunk_id+1}] Esperando un minuto más...")
                time.sleep(60)
            
            if login_success:
                break
                
            # Si no tuvo éxito y hay más intentos, ofrecer reintentar
            if attempt < max_attempts - 1:
                resp = input(f"[Agente {chunk_id+1}] ¿Deseas intentar iniciar sesión de nuevo? (s/n): ")
                if resp.lower() != 's':
                    break
        
        # Si después de todos los intentos no se pudo iniciar sesión, abortar
        if not login_success:
            print(f"[Agente {chunk_id+1}] No se pudo iniciar sesión después de {max_attempts} intentos. Abortando.")
            driver.quit()
            return
            
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
        driver.quit()
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
    parser = argparse.ArgumentParser(description="Descargador paralelo de imágenes de Forgotten Realms Wiki")
    parser.add_argument("--agents", type=int, default=4, 
                        help="Número de agentes paralelos (default: 4)")
    parser.add_argument("--failed", type=str, 
                        help="Archivo de lista de archivos fallidos para reintentar")
    args = parser.parse_args()
    
    num_agents = args.agents
    
    # Cargar lista de archivos
    if args.failed:
        print(f"Cargando archivos fallidos de {args.failed}")
        with open(args.failed, "r", encoding="utf-8") as f:
            filenames = f.read().splitlines()
    else:
        print("Cargando lista completa de archivos...")
        with open("Filenames.txt", "r", encoding="utf-8") as f:
            filenames = f.read().splitlines()
    
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
            args=(i, file_chunks[i]),
            name=f"Agente-{i+1}"
        )
        processes.append(p)
        p.start()
    
    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()
    
    print("¡Todos los agentes han completado su trabajo!")
    print("Comprueba los archivos de registro para ver los detalles de los archivos fallidos.")
