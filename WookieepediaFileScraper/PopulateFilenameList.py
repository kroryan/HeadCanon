import requests
import lxml
import bs4
import time

URL = "https://forgottenrealms.fandom.com/wiki/Special:AllPages?namespace=6&from="

first_filename = ""
last_title = ""

while 1:
    try:
        # Añadir un pequeño retraso para evitar solicitudes demasiado rápidas
        time.sleep(1)
        source = requests.get(URL + first_filename).text
        soup = bs4.BeautifulSoup(source, "lxml")
        chunk = soup.find("ul", {"class": "mw-allpages-chunk"})
          # Verificar si se encontró el elemento chunk
        if chunk is None:
            print("No se encontró el elemento 'mw-allpages-chunk' en la URL actual.")
            # Intentar avanzar a la siguiente letra si es posible
            if last_title:
                print(f"Intentando avanzar a partir de: {last_title}")
                # Avanzar a la siguiente letra del alfabeto
                first_filename = last_title[5:] + chr(ord(first_filename[-1]) + 1 if first_filename else ord('a'))
                print(f"Nueva URL: {URL + first_filename}")
            else:
                # Si no tenemos un último título, intentemos con una letra
                if not first_filename:
                    first_filename = "a"
                else:
                    # Avanzar a la siguiente letra
                    first_filename = chr(ord(first_filename[0]) + 1)
                print(f"Intentando con la letra: {first_filename}")
            continue
            
        with open("Filenames.txt", "a", encoding="utf-8") as f:
            for item in chunk.contents:
               if item != "\n":
                    try:
                        last_title = item.contents[0]["title"]
                        print(last_title)
                        f.write(last_title + "\n")
                    except (IndexError, KeyError) as e:
                        print(f"Error procesando un elemento: {e}")
                        continue
        
        if len(chunk.contents) >= 5:
            first_filename = last_title[5:] + "a"
        else:
            break
    except Exception as e:
        print(f"Error general: {e}")
        print("Intentando de nuevo en 10 segundos...")
        time.sleep(10)
        continue
