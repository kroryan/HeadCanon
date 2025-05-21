# Wiki Image Scraper / Descargador de Imágenes Wiki

[English](#english) | [Español](#español)

<a name="english"></a>
# English

A tool for downloading all images from Wookieepedia or Forgotten Realms Wiki. PLEASE USE THE SCRAPER SIN (NO) LOGIN

Make sure you have at least 50 GB of free disk space to accommodate all the files!

## Download Options

After several experiments, we now have multiple scripts for different situations. **We recommend using the "no login" method** as it's simpler and doesn't require credentials.

### Method 1: No Login (Recommended)
This method doesn't require a Fandom account and downloads images directly.

```powershell
python Scraper_Sin_Login.py
```

### Method 2: Chrome Profile
This method uses your already authenticated Chrome profile, avoiding captcha issues.

```powershell
python Scraper_Chrome_Profile.py
```

### Method 3: Simple Version
A simplified version without parallel processing for systems with fewer resources.

```powershell
python Scraper_Simple.py
```

### Method 4: Original (Not Recommended)
The original method that requires credentials and solving captchas.

```powershell
python Scraper.py
```

## How to Use (Recommended Workflow)

1. **Get file list:**
   ```powershell
   python PopulateFilenameList.py
   ```
   This will create a file called `Filenames.txt`.

2. **Download images without login:**
   ```powershell
   python Scraper_Sin_Login.py
   ```
   No credentials required, works automatically.

3. **Check for missing files:**
   ```powershell
   python Check_Missing_Files.py
   ```
   This will generate a `missing.txt` file with images that failed to download.

4. **Download only missing files:**
   ```powershell
   python Scraper_Sin_Login.py --failed missing.txt
   ```

5. **Check image integrity:**
   ```powershell
   python Check_Image_Integrity.py
   ```
   This will verify all downloaded images and create lists of corrupted or damaged files.

## Important Notes

- **Download errors:** After a long running time, some files may not download correctly. This is normal and you can use `Check_Missing_Files.py` to identify them.

- **Connection issues:** If the script stops, you can restart it at any time. It won't re-download existing files.

- **Download time:** The complete process can take several days depending on your connection and the number of files.

## Image Integrity Verification

The `Check_Image_Integrity.py` script helps verify the integrity of downloaded images:

1. Checks if images can be opened correctly with PIL
2. Identifies corrupted or damaged images
3. Creates a list of files that need to be downloaded again
4. Allows you to download only the damaged images
5. Shows results in real-time as it finds corrupted files

### Basic Usage

```powershell
python Check_Image_Integrity.py
```

### Advanced Options

```powershell
python Check_Image_Integrity.py --output "damaged.txt" --files-dir "MyFiles" --check-all
```

- `--output`: Name of the file where the list of corrupted files will be saved (default: "corrupted_files.txt")
- `--files-dir`: Name of the directory where downloaded files are stored (default: "Files")
- `--check-all`: Check all files against the web (slower but more accurate)

### Key Features

- **Real-time Results**: Displays corrupted files immediately as they are found
- **Progress Tracking**: Shows verification progress with estimated time remaining
- **Timestamped Logs**: Creates detailed logs with date and time for each verification run
- **Clean Interface**: Shows only problem files, no clutter from normal operations
- **Real-time Saving**: Saves corrupted file list as it goes, so you don't lose results if the process is interrupted

The script automatically scans your Files directory and checks only the images you actually have downloaded, without needing a separate file list.

## Missing Files Checker

The `Check_Missing_Files.py` script compares the files listed in `Filenames.txt` with the files actually downloaded in the `Files` folder, and generates a `missing.txt` file with the list of files that still need to be downloaded.

### Basic Usage

```powershell
python Check_Missing_Files.py
```

### Options

```powershell
python Check_Missing_Files.py --filenames "my_list.txt" --output "missing.txt" --files-dir "MyFiles"
```

- `--filenames`: Name of the file containing the complete list of files to download (default: "Filenames.txt")
- `--output`: Name of the file where the list of missing files will be saved (default: "missing.txt")
- `--files-dir`: Name of the directory where downloaded files are stored (default: "Files")

## Requirements

Install all necessary dependencies:
```powershell
pip install -r requirements.txt
```

## Troubleshooting

- **WebDriver error**: Make sure Chrome is installed and update dependencies
- **Slow download or 429 errors**: The site may be limiting requests. Increase wait times to avoid blocks
- **Image not found errors**: Some images may not be available or have a different HTML structure
- **Connection failures**: Check your internet connection and try again
- **Error loading Filenames.txt**: Make sure the file exists and has the correct format
- **Error scanning Files directory**: Verify that the downloaded files folder exists

<a name="español"></a>
# Español

Una herramienta para descargar todas las imágenes de Wookieepedia o Forgotten Realms Wiki.

¡Asegúrate de tener al menos 50 GB de espacio libre en disco para almacenar todos los archivos!

## Opciones de descarga

Después de varios experimentos, ahora tenemos múltiples scripts para diferentes situaciones. **Recomendamos usar el método sin login** ya que es más sencillo y no requiere credenciales.

### Método 1: Sin Login (Recomendado)
Este método no requiere cuenta de Fandom y descarga las imágenes directamente.

```powershell
python Scraper_Sin_Login.py
```

### Método 2: Con Perfil de Chrome
Este método usa tu perfil de Chrome ya autenticado, evitando problemas de captcha.

```powershell
python Scraper_Chrome_Profile.py
```

### Método 3: Versión Simple
Una versión simplificada sin procesamiento paralelo para equipos con menos recursos.

```powershell
python Scraper_Simple.py
```

### Método 4: Original (No recomendado)
El método original que requiere credenciales y resolver captchas.

```powershell
python Scraper.py
```

## Cómo usar (Flujo recomendado)

1. **Obtener lista de archivos:**
   ```powershell
   python PopulateFilenameList.py
   ```
   Esto creará un archivo llamado `Filenames.txt`.

2. **Descargar imágenes sin login:**
   ```powershell
   python Scraper_Sin_Login.py
   ```
   No requiere credenciales y funciona automáticamente.

3. **Verificar archivos faltantes:**
   ```powershell
   python Check_Missing_Files.py
   ```
   Esto generará un archivo `missing.txt` con las imágenes que faltan por descargar.

4. **Descargar solo los archivos faltantes:**
   ```powershell
   python Scraper_Sin_Login.py --failed missing.txt
   ```

5. **Verificar integridad de imágenes:**
   ```powershell
   python Check_Image_Integrity.py
   ```
   Esto verificará todas las imágenes descargadas y creará listas de archivos corruptos o dañados.

## Notas importantes

- **Errores de descarga:** Después de mucho tiempo de ejecución, es posible que algunos archivos no se descarguen correctamente. Esto es normal y puedes usar `Check_Missing_Files.py` para identificarlos.

- **Problemas de conexión:** Si el script se detiene, puedes reiniciarlo en cualquier momento. No volverá a descargar archivos ya existentes.

- **Tiempo de descarga:** El proceso completo puede llevar varios días dependiendo de tu conexión y la cantidad de archivos.

## Verificación de integridad de imágenes

El script `Check_Image_Integrity.py` ayuda a verificar la integridad de las imágenes descargadas:

1. Comprueba si las imágenes se pueden abrir correctamente con PIL
2. Identifica imágenes corruptas o dañadas
3. Crea una lista de archivos que necesitan ser descargados nuevamente
4. Permite descargar solo las imágenes dañadas
5. Muestra resultados en tiempo real a medida que encuentra archivos corruptos

### Uso básico

```powershell
python Check_Image_Integrity.py
```

### Opciones avanzadas

```powershell
python Check_Image_Integrity.py --output "dañados.txt" --files-dir "MisArchivos" --check-all
```

- `--output`: Nombre del archivo donde se guardará la lista de archivos corruptos (por defecto: "corrupted_files.txt")
- `--files-dir`: Nombre del directorio donde se almacenan los archivos descargados (por defecto: "Files")
- `--check-all`: Verificar todos los archivos contra la web (más lento pero más preciso)

### Características principales

- **Resultados en tiempo real**: Muestra los archivos corruptos inmediatamente cuando son encontrados
- **Seguimiento del progreso**: Muestra el avance de la verificación con tiempo estimado restante
- **Registros con fecha y hora**: Crea logs detallados con fecha y hora para cada ejecución
- **Interfaz limpia**: Muestra solo archivos con problemas, sin información innecesaria
- **Guardado en tiempo real**: Guarda la lista de archivos corruptos sobre la marcha, para no perder resultados si el proceso se interrumpe

El script escanea automáticamente tu directorio Files y verifica solo las imágenes que realmente has descargado, sin necesidad de una lista de archivos separada.

## Verificador de archivos faltantes

El script `Check_Missing_Files.py` compara los archivos listados en `Filenames.txt` con los archivos realmente descargados en la carpeta `Files`, y genera un archivo `missing.txt` con la lista de archivos que faltan por descargar.

### Uso básico

```powershell
python Check_Missing_Files.py
```

### Opciones

```powershell
python Check_Missing_Files.py --filenames "mi_lista.txt" --output "faltantes.txt" --files-dir "MisArchivos"
```

- `--filenames`: Nombre del archivo que contiene la lista completa de archivos a descargar (por defecto: "Filenames.txt")
- `--output`: Nombre del archivo donde se guardará la lista de archivos faltantes (por defecto: "missing.txt")
- `--files-dir`: Nombre del directorio donde se almacenan los archivos descargados (por defecto: "Files")

## Requisitos

Instala todas las dependencias necesarias:
```powershell
pip install -r requirements.txt
```

## Solución de problemas

- **Error al iniciar el WebDriver**: Asegúrate de tener instalado Chrome y las dependencias necesarias
- **Descarga lenta o errores 429**: El sitio puede estar limitando las peticiones. Aumenta los tiempos de espera para evitar bloqueos
- **Errores de imagen no encontrada**: Algunas imágenes pueden no estar disponibles o tener una estructura HTML diferente
- **Fallos de conexión**: Verifica tu conexión a internet y vuelve a intentarlo
- **Error al cargar Filenames.txt**: Asegúrate de que el archivo existe y tiene el formato correcto
- **Error al escanear directorio Files**: Verifica que existe la carpeta de archivos descargados
