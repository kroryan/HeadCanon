# Compares images on Project HeadCanon with images on Wookieepedia using their SHA-1 hashes.
# If the hashes are different, downloads the file from Wookieepedia.
# If no file exists on Wookieepedia with the same name, adds it to a file.

import requests

base_url = "http://192.168.1.11:1138"   # Base URL of the wiki
limit = 500                             # Go by groups of this many articles

params = {
    "action": "query",
    "list": "allimages",
    "aisort": "name",
    "ailimit": str(limit),
    "aiprop": "sha1",
    "format": "json",
}

wp_params = {
    "action": "query",
    "list": "allimages",
    "aisort": "name",
    "ailimit": "1",
    "aiprop": "sha1|url",
    "format": "json"
}

while 1:
    r = requests.get(url=base_url + "/api.php", params=params)
    data = r.json()
    file_list = data['query']['allimages']

    for p in file_list:
        hc_name = p['name']
        hc_sha1 = p['sha1']

        wp_params['aifrom'] = hc_name

        wp_r = requests.get(url="https://starwars.fandom.com/api.php", params = wp_params)
        wp_data = wp_r.json()
        wp_file = wp_data['query']['allimages'][0]

        wp_name = wp_file['name']
        wp_sha1 = wp_file['sha1']
        wp_url = wp_file['url']

        if wp_name != hc_name:
            with open("FilesNotOnWookieepedia.txt", "a", encoding="utf-8") as f:
                f.write(hc_name + "\n")
            f.close()
            print("Wookieepedia has no file called " + hc_name + "!")
        
        elif wp_sha1 != hc_sha1:
            print(hc_name + " has a different hash on Wookieepedia. Downloading...")
            dl_r = requests.get(url=wp_url)
            with open("FilesWithDifferentHashes/" + hc_name, "wb") as f:
                f.write(dl_r.content)
            f.close()
            print("Done!")
        
        else:
            print(hc_name)

    if 'continue' in data:
        params['aicontinue'] = data['continue']['aicontinue']
    else:
        break