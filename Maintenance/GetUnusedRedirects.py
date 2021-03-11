import requests
import lxml
import bs4

# Get a list of the names of all articles listed on the wiki's Special:UnusedRedirects page

base_url = "http://192.168.1.20:1138"
out_file_path = "UnusedRedirects.txt"
offset = 0
limit = 500

url = base_url + "/index.php?title=Special:UnusedRedirects&limit="

while 1:
    source = requests.get(url + str(limit) + "&offset=" + str(offset)).text
    soup = bs4.BeautifulSoup(source, "lxml")
    chunk = soup.find_all("a", {"class": "mw-redirect"})

    with open(out_file_path, "a", encoding="utf-8") as f:

        for item in chunk:
            f.write(item["title"] + "\n")
            print(item["title"])
    
    f.close()
    
    if len(chunk) == 0:
        break
    else:
        offset += limit
