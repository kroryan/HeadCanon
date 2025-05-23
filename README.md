# HeadCanon - Tools for Wiki Management and Scraping

## English
HeadCanon is a collection of tools for managing wiki content, particularly for the Forgotten Realms Wiki. This repository contains various utilities for maintaining wiki articles, processing images, and scraping content.

### Project Structure

- **Maintenance**: Scripts for wiki maintenance tasks
  - `CompareImages.py`: Compare images to identify duplicates
  - `GetArticlesFromCategory.py`: Extract articles from specific categories
  - `GetPagesFromQuery.py`: Retrieve pages based on search queries
  - `GetUnusedRedirects.py`: Find redirects that are not being used

- **Pages**: CSS and JS templates for wiki customization
  - Various MediaWiki customization files for Cosmos, Monobook themes
  - Infobox styling and colors
  - Module templates

- **PyWikiBot userscripts**: Automation scripts using PyWikiBot
  - `add_top_tag_based_on_appearances.py`: Add tags based on content appearances
  - `fix_used_redirects.py`: Fix or update redirects
  - `rename_legends.py`: Rename pages following a specific pattern

- **WookieepediaFileScraper**: Tool for downloading images from Forgotten Realms Wiki
  - See the dedicated README in this folder for detailed instructions

### Getting Started

1. Install Python 3.7+ if not already installed
2. Install dependencies for the specific tool you want to use:
   ```powershell
   cd path\to\tool
   pip install -r requirements.txt
   ```
3. Follow the instructions in each tool's directory for specific usage

### Requirements

- Python 3.7+
- Required packages are listed in each tool's requirements.txt file
- Some tools may require authentication to wikis

## Español
HeadCanon es una colección de herramientas para la gestión de contenido wiki, particularmente para el Wiki de Forgotten Realms. Este repositorio contiene varias utilidades para mantenimiento de artículos, procesamiento de imágenes y extracción de contenido.

### Estructura del Proyecto

- **Maintenance**: Scripts para tareas de mantenimiento wiki
  - `CompareImages.py`: Compara imágenes para identificar duplicados
  - `GetArticlesFromCategory.py`: Extrae artículos de categorías específicas
  - `GetPagesFromQuery.py`: Recupera páginas basadas en consultas de búsqueda
  - `GetUnusedRedirects.py`: Encuentra redirecciones que no están siendo utilizadas

- **Pages**: Plantillas CSS y JS para personalización wiki
  - Varios archivos de personalización MediaWiki para temas Cosmos y Monobook
  - Estilo y colores para infoboxes
  - Plantillas de módulos

- **PyWikiBot userscripts**: Scripts de automatización usando PyWikiBot
  - `add_top_tag_based_on_appearances.py`: Añade etiquetas basadas en apariciones de contenido
  - `fix_used_redirects.py`: Arregla o actualiza redirecciones
  - `rename_legends.py`: Renombra páginas siguiendo un patrón específico

- **WookieepediaFileScraper**: Herramienta para descargar imágenes del Wiki de Forgotten Realms
  - Consulta el README dedicado en esta carpeta para instrucciones detalladas

### Primeros Pasos

1. Instala Python 3.7+ si aún no lo tienes instalado
2. Instala las dependencias para la herramienta específica que deseas usar:
   ```powershell
   cd ruta\a\la\herramienta
   pip install -r requirements.txt
   ```
3. Sigue las instrucciones en el directorio de cada herramienta para su uso específico

### Requisitos

- Python 3.7+
- Los paquetes requeridos están listados en el archivo requirements.txt de cada herramienta
- Algunas herramientas pueden requerir autenticación a wikis
