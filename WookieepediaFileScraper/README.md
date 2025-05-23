# Forgotten Realms Wiki Image Scraper

## English

A tool for downloading images from the Forgotten Realms Wiki. This utility helps you collect all image files for offline access, archival purposes, or content analysis.

### Features

- Automatically collects image filenames from Forgotten Realms Wiki
- Downloads images with proper metadata preservation
- Handles login process through Fandom's authentication system
- Automatically retries on connection errors
- Skips files that can't be found or accessed

### Requirements

- Python 3.7 or higher
- Chrome browser installed
- Internet connection
- At least 50 GB of free disk space (for complete archive)

### Installation

1. Install the required Python packages:
```powershell
pip install -r requirements.txt
```

### Usage

#### Option 1: Using the Batch File (Recommended)

Simply run the included batch file by double-clicking `ejecutar_descarga.bat`. This will:
- Install required dependencies
- Generate the list of filenames if it doesn't exist
- Start the download process

#### Option 2: Manual Execution

1. First, generate the list of image filenames:
```powershell
python PopulateFilenameList.py
```

2. Edit the `Scraper.py` file to add your Fandom account credentials:
   - Replace `USERNAME` and `PASSWORD` variables with your Fandom login details

3. Run the scraper:
```powershell
python Scraper.py
```

4. Complete any CAPTCHA if prompted, then press Enter in the terminal to begin downloading

5. Wait for the downloads to complete (this may take several days for a complete archive)

### Troubleshooting

- **SSL Errors**: The script is configured to handle SSL certificate issues. If you still encounter problems, make sure your Python installation has up-to-date certificates.
- **Login Issues**: If automatic login fails, the script will prompt you to log in manually in the opened browser window.
- **Missing Images**: Some images may no longer exist on the wiki; the script will skip these and continue.

## Español

Una herramienta para descargar imágenes del Wiki de Forgotten Realms. Esta utilidad te ayuda a recopilar todos los archivos de imágenes para acceso offline, propósitos de archivo o análisis de contenido.

### Características

- Recopila automáticamente nombres de archivos de imágenes del Wiki de Forgotten Realms
- Descarga imágenes con preservación adecuada de metadatos
- Gestiona el proceso de inicio de sesión a través del sistema de autenticación de Fandom
- Reintenta automáticamente en caso de errores de conexión
- Omite archivos que no se pueden encontrar o acceder

### Requisitos

- Python 3.7 o superior
- Navegador Chrome instalado
- Conexión a Internet
- Al menos 50 GB de espacio libre en disco (para un archivo completo)

### Instalación

1. Instala los paquetes de Python requeridos:
```powershell
pip install -r requirements.txt
```

### Uso

#### Opción 1: Usando el Archivo Batch (Recomendado)

Simplemente ejecuta el archivo batch incluido haciendo doble clic en `ejecutar_descarga.bat`. Esto:
- Instalará las dependencias requeridas
- Generará la lista de nombres de archivo si no existe
- Iniciará el proceso de descarga

#### Opción 2: Ejecución Manual

1. Primero, genera la lista de nombres de archivos de imágenes:
```powershell
python PopulateFilenameList.py
```

2. Edita el archivo `Scraper.py` para añadir tus credenciales de Fandom:
   - Reemplaza las variables `USERNAME` y `PASSWORD` con tus datos de inicio de sesión de Fandom

3. Ejecuta el scraper:
```powershell
python Scraper.py
```

4. Completa cualquier CAPTCHA si se solicita, luego presiona Enter en la terminal para comenzar la descarga

5. Espera a que se completen las descargas (esto puede tomar varios días para un archivo completo)

### Solución de problemas

- **Errores SSL**: El script está configurado para manejar problemas de certificados SSL. Si aún encuentras problemas, asegúrate de que tu instalación de Python tenga certificados actualizados.
- **Problemas de inicio de sesión**: Si el inicio de sesión automático falla, el script te pedirá que inicies sesión manualmente en la ventana del navegador abierta.
- **Imágenes faltantes**: Algunas imágenes pueden ya no existir en el wiki; el script las omitirá y continuará.

## Technical Details

### How the Script Works

1. **PopulateFilenameList.py**:
   - Crawls the Special:AllPages section of Forgotten Realms Wiki for the File: namespace
   - Extracts filenames and saves them to Filenames.txt
   - Uses incremental crawling to navigate through all pages
   - Implements error handling and retry logic for network issues

2. **Scraper.py**:
   - Reads filenames from the generated list
   - Handles authentication to Fandom using Selenium WebDriver
   - For each file:
     - Opens the file's wiki page
     - Extracts the direct URL to the full-resolution image
     - Downloads the image using requests library
     - Saves it to the local Files directory
   - Implements robust error handling for network and SSL issues
