import os
import logging
import argparse
from tqdm import tqdm

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("check_missing.log"),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description="Verificador de archivos faltantes en la descarga")
    parser.add_argument("--filenames", type=str, default="Filenames.txt", 
                        help="Archivo con la lista completa de archivos a descargar (default: Filenames.txt)")
    parser.add_argument("--output", type=str, default="missing.txt", 
                        help="Archivo de salida con la lista de archivos faltantes (default: missing.txt)")
    parser.add_argument("--files-dir", type=str, default="Files", 
                        help="Directorio donde se almacenan los archivos descargados (default: Files)")
    args = parser.parse_args()

    # Verificar que el archivo de filenames existe
    if not os.path.exists(args.filenames):
        logging.error(f"Error: No se encontró el archivo '{args.filenames}'")
        logging.error("Por favor, asegúrate de que existe el archivo con la lista de archivos a descargar.")
        return

    # Verificar que el directorio de archivos existe
    if not os.path.exists(args.files_dir):
        logging.error(f"Error: No se encontró el directorio '{args.files_dir}'")
        logging.error("Por favor, asegúrate de que existe el directorio de archivos descargados.")
        return

    # Cargar la lista completa de archivos
    logging.info(f"Cargando lista de archivos desde '{args.filenames}'...")
    with open(args.filenames, "r", encoding="utf-8") as f:
        filenames = f.read().splitlines()

    total_files = len(filenames)
    logging.info(f"Se encontraron {total_files} archivos en la lista.")

    # Obtener lista de archivos ya descargados
    logging.info(f"Escaneando archivos descargados en '{args.files_dir}'...")
    downloaded_files = set(os.listdir(args.files_dir))
    logging.info(f"Se encontraron {len(downloaded_files)} archivos descargados.")

    # Buscar archivos faltantes
    missing_files = []
    for filename in tqdm(filenames, desc="Verificando archivos"):
        # Sanitizar el nombre del archivo como se hace en el script de descarga
        safe_filename = filename.replace('"', '_').replace('?', '_').replace('/', '_').replace('\\', '_')
        # El nombre del archivo descargado no incluye el prefijo "File:"
        expected_filename = safe_filename[5:] if safe_filename.startswith("File:") else safe_filename
        
        if expected_filename not in downloaded_files:
            missing_files.append(filename)

    # Guardar la lista de archivos faltantes
    if missing_files:
        with open(args.output, "w", encoding="utf-8") as f:
            for filename in missing_files:
                f.write(f"{filename}\n")
        
        logging.info(f"Se encontraron {len(missing_files)} archivos faltantes.")
        logging.info(f"Lista de archivos faltantes guardada en '{args.output}'.")
        logging.info(f"Puedes usar este archivo para descargar los archivos faltantes:")
        logging.info(f"python Scraper_Sin_Login.py --failed {args.output}")
    else:
        logging.info("¡Felicidades! Todos los archivos han sido descargados correctamente.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Proceso interrumpido por el usuario.")
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
