@echo off
echo =====================================================
echo Script para descarga de imágenes de Forgotten Realms Wiki
echo =====================================================

echo Instalando dependencias necesarias...
pip install -r requirements.txt

echo.
echo Verificando si hay que generar la lista de archivos...
if not exist "Filenames.txt" (
    echo Generando lista de archivos...
    python PopulateFilenameList.py
) else (
    echo Lista de archivos ya existe. Procediendo a descarga...
)

echo.
echo Iniciando proceso de descarga...
python Scraper.py

echo.
echo Proceso completado.
pause
