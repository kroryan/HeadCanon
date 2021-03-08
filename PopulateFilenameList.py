import requests
import lxml
import bs4

URL = "https://starwars.fandom.com/wiki/Special:AllPages?namespace=6&from="

first_filename = ""
last_title = ""

while 1:
    source = requests.get(URL + first_filename).text
    soup = bs4.BeautifulSoup(source, "lxml")
    chunk = soup.find("ul", {"class": "mw-allpages-chunk"})
    with open("Filenames.txt", "a", encoding="utf-8") as f:
        for item in chunk.contents:
           if item != "\n":
                last_title = item.contents[0]["title"]
                print(last_title)
                f.write(last_title + "\n")
    f.close()
    if len(chunk.contents) >= 5:
        first_filename = last_title[5:] + "a"
    else:
        break