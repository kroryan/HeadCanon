import requests
import lxml
import bs4
import time

# Update URL to use the Star Wars wiki instead of Forgotten Realms
URL = "https://starwars.fandom.com/wiki/Special:AllPages?namespace=6&from="

first_filename = ""
last_title = ""

while 1:
    try:
        # Add a delay to be respectful to the server
        time.sleep(1)
        
        print(f"Fetching files from: {URL + first_filename}")
        response = requests.get(URL + first_filename)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        source = response.text
        soup = bs4.BeautifulSoup(source, "lxml")
        chunk = soup.find("ul", {"class": "mw-allpages-chunk"})
        
        # Check if chunk exists before proceeding
        if chunk is None:
            print("No more files found or page structure has changed. Exiting.")
            break
            
        with open("Filenames.txt", "a", encoding="utf-8") as f:
            for item in chunk.contents:
                if item != "\n":
                    last_title = item.contents[0]["title"]
                    print(last_title)
                    f.write(last_title + "\n")
        
        # Check if we have enough items to continue to the next page
        if len(chunk.contents) >= 5:
            first_filename = last_title[5:] + "a"
        else:
            print("Reached end of file list. Exiting.")
            break
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        # If there's still an error after retrying, maybe we should stop
        try:
            response = requests.get(URL + first_filename)
            response.raise_for_status()
        except Exception:
            print("Retry failed. Exiting to prevent further errors.")
            break
