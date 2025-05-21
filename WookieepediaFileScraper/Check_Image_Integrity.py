import os
import hashlib
import requests
import bs4
import lxml
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from tqdm import tqdm
from PIL import Image
import io
import datetime
import json

# Configurar logging
log_filename = f"check_integrity_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# Base URL para la wiki
FILE_URL_BASE = "https://forgottenrealms.fandom.com/wiki/"

def calculate_file_hash(file_path):
    """Calcula el hash MD5 de un archivo"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error al calcular hash para {file_path}: {str(e)}")
        return None

def is_image_valid(file_path):
    """Verifica si una imagen puede abrirse correctamente con PIL"""
    try:
        img = Image.open(file_path)
        img.verify()  # Verifica la integridad de la imagen
        return True
    except Exception as e:
        logging.warning(f"Imagen inválida: {file_path} - {str(e)}")
        return False

def get_online_image_info(driver, filename):
    """Obtiene información sobre la imagen en línea"""
    try:
        # Preparar el nombre para la URL 
        # Si no comienza con 'File:', añadirlo
        if not filename.startswith("File:"):
            url_filename = "File:" + filename
        else:
            url_filename = filename
            
        url_string = FILE_URL_BASE + url_filename
        logging.debug(f"Consultando URL: {url_string}")
        driver.get(url_string)
        time.sleep(random.uniform(0.5, 2.0))
        
        source = driver.page_source
        soup = bs4.BeautifulSoup(source, "lxml")
        
        # Buscar la URL de la imagen original
        url_tag = soup.find(property="og:image")
        if not url_tag:
            img_div = soup.find('div', class_='fullImageLink')
            if img_div and img_div.find('a'):
                image_url = img_div.find('a')['href']
            else:
                return None, None
        else:
            image_url = url_tag["content"]
        
        # Obtener información del tamaño de la imagen
        size_info = soup.find('div', class_='fullMedia')
        file_size = None
        if size_info:
            size_text = size_info.text
            # Extraer el tamaño del texto (ej: "1,024 × 768 (241 KB)")
            import re
            match = re.search(r'\((\d+(?:\.\d+)?\s*(?:KB|MB|B|GB))\)', size_text)
            if match:
                file_size = match.group(1)
        
        return image_url, file_size
    except Exception as e:
        logging.error(f"Error al obtener info online para {filename}: {str(e)}")
        return None, None

def get_local_files(files_dir="Files"):
    """Obtiene la lista de archivos que existen localmente"""
    try:
        if not os.path.exists(files_dir):
            logging.error(f"Error: No se encontró el directorio '{files_dir}'")
            return []
            
        local_files = os.listdir(files_dir)
        logging.info(f"Se encontraron {len(local_files)} archivos en el directorio '{files_dir}'")
        return local_files
    except Exception as e:
        logging.error(f"Error al obtener archivos locales: {str(e)}")
        return []

def load_verified_files(verified_file="verified_files.json"):
    """Carga la lista de archivos verificados previamente"""
    try:
        if os.path.exists(verified_file):
            with open(verified_file, "r", encoding="utf-8") as f:
                verified = json.load(f)
                logging.info(f"Se cargaron {len(verified)} archivos previamente verificados")
                return verified
        return {}
    except Exception as e:
        logging.error(f"Error al cargar archivos verificados: {str(e)}")
        return {}

def check_images_integrity(local_files, files_dir="Files", check_all=False):
    """Verifica la integridad de las imágenes descargadas"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    
    corrupted_files = []
    checked_count = 0
    checked_with_web = 0
    start_time = time.time()
    
    # Crear un archivo para ir guardando los resultados en tiempo real
    results_filename = f"corrupted_files_progress_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        
        progress_bar = tqdm(total=len(local_files), desc="Verificando archivos")
        
        for filename in local_files:
            checked_count += 1
            progress_bar.update(1)
            
            # Actualizar la descripción de la barra de progreso con estadísticas
            if checked_count % 10 == 0:
                elapsed = time.time() - start_time
                files_per_second = checked_count / elapsed if elapsed > 0 else 0
                eta = (len(local_files) - checked_count) / files_per_second if files_per_second > 0 else 0
                progress_bar.set_description(
                    f"Verificados: {checked_count}/{len(local_files)} | "
                    f"Corruptos: {len(corrupted_files)} | "
                    f"ETA: {int(eta/60)} min"
                )
            
            file_path = os.path.join(files_dir, filename)
            
            # Verificar integridad básica de la imagen
            if not is_image_valid(file_path):
                corrupted_name = f"File:{filename}"
                corrupted_files.append(corrupted_name)
                
                # Guardar en tiempo real y mostrar solo archivos con problemas
                print(f"\n❌ Archivo corrupto: {filename}")
                logging.error(f"Archivo corrupto: {filename}")
                
                with open(results_filename, "a", encoding="utf-8") as f:
                    f.write(f"{corrupted_name}\n")
                
                continue
                
            # Verificación avanzada contra la versión en línea (opcional)
            if check_all or random.random() < 0.1:
                checked_with_web += 1
                image_url, online_size = get_online_image_info(driver, filename)
                if not image_url:
                    continue
                
                try:
                    # Verificar el tamaño del archivo local
                    local_size = os.path.getsize(file_path)
                    
                    # Verificar si hay una discrepancia significativa en el tamaño
                    if online_size:
                        try:
                            size_num = float(online_size.split()[0].replace(',', ''))
                            size_unit = online_size.split()[1] if len(online_size.split()) > 1 else "B"
                            expected_size = size_num * {'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}[size_unit]
                            
                            # Si la diferencia es más del 10%, marcar como sospechoso
                            if abs(local_size - expected_size) / expected_size > 0.1:
                                corrupted_name = f"File:{filename}"
                                if corrupted_name not in corrupted_files:
                                    corrupted_files.append(corrupted_name)
                                    
                                    # Guardar en tiempo real y mostrar solo archivos con problemas
                                    print(f"\n⚠️ Discrepancia de tamaño: {filename}")
                                    print(f"   Local: {local_size} bytes | Online: ~{int(expected_size)} bytes")
                                    logging.warning(f"Discrepancia de tamaño en {filename}: local={local_size}, online~{expected_size}")
                                    
                                    with open(results_filename, "a", encoding="utf-8") as f:
                                        f.write(f"{corrupted_name}\n")
                        except (ValueError, KeyError, IndexError) as e:
                            logging.error(f"Error al analizar tamaño para {filename}: {str(e)}")
                except Exception as e:
                    logging.error(f"Error al verificar tamaño para {filename}: {str(e)}")
        
        # Cerrar la barra de progreso
        progress_bar.close()
    
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
    finally:
        driver.quit()
    
    # Resumen final
    logging.info(f"Archivos verificados: {checked_count}/{len(local_files)}")
    logging.info(f"Archivos verificados contra la web: {checked_with_web}")
    logging.info(f"Archivos corruptos encontrados: {len(corrupted_files)}")
    logging.info(f"Tiempo total: {time.time() - start_time:.2f} segundos")
    
    return corrupted_files

def main():
    parser = argparse.ArgumentParser(description="Verificador de integridad de imágenes descargadas")
    parser.add_argument("--output", type=str, default="corrupted_files.txt", 
                        help="Archivo de salida con la lista de archivos corruptos (default: corrupted_files.txt)")
    parser.add_argument("--files-dir", type=str, default="Files", 
                        help="Directorio donde se almacenan los archivos descargados (default: Files)")
    parser.add_argument("--check-all", action="store_true",
                        help="Verificar todos los archivos contra la web (más lento pero más preciso)")
    args = parser.parse_args()

    print(f"📊 Verificador de integridad de imágenes - Logs guardados en: {log_filename}")
    print("📝 Los resultados se guardarán a medida que se encuentren problemas")
    print("⚠️ Solo se mostrarán en pantalla los archivos con problemas")
    print("--------------------------------------------------")

    # Verificar que el directorio de archivos existe
    if not os.path.exists(args.files_dir):
        logging.error(f"Error: No se encontró el directorio '{args.files_dir}'")
        print(f"❌ Error: No se encontró el directorio '{args.files_dir}'")
        return

    # Obtener lista de archivos locales
    local_files = get_local_files(args.files_dir)
    if not local_files:
        logging.error("No se encontraron archivos para verificar.")
        print("❌ No se encontraron archivos para verificar.")
        return

    logging.info(f"Se verificarán {len(local_files)} archivos descargados.")
    print(f"🔍 Se verificarán {len(local_files)} archivos descargados...")
    print("--------------------------------------------------")
    
    # Comprobar integridad
    corrupted_files = check_images_integrity(local_files, args.files_dir, args.check_all)
    
    # Guardar resultados finales
    if corrupted_files:
        with open(args.output, "w", encoding="utf-8") as f:
            for filename in corrupted_files:
                f.write(f"{filename}\n")
        print("\n--------------------------------------------------")
        print(f"📋 Se encontraron {len(corrupted_files)} archivos con problemas.")
        print(f"💾 Lista completa guardada en '{args.output}'")
        print(f"🔄 Puedes descargar nuevamente estos archivos con:")
        print(f"   python Scraper_Sin_Login.py --failed {args.output}")
        
        logging.info(f"Se encontraron {len(corrupted_files)} archivos corruptos. Lista guardada en '{args.output}'")
        logging.info(f"Puedes descargar nuevamente estos archivos con: python Scraper_Sin_Login.py --failed {args.output}")
    else:
        print("\n--------------------------------------------------")
        print("✅ No se encontraron archivos corruptos.")
        logging.info("No se encontraron archivos corruptos.")
    
    # Resumen final
    if not corrupted_files:
        print("🎉 ¡Felicidades! Todos los archivos parecen estar en buen estado.")
        logging.info("¡Felicidades! Todos los archivos parecen estar en buen estado.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Proceso interrumpido por el usuario.")
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
