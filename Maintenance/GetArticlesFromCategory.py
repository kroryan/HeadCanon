# Grabs a list of articles in the specified namespace belonging to the specified category

import requests

base_url = "http://192.168.1.20:1138"   # Base URL of the wiki
category_name = "Real-world articles"   # Name of the category to search
namespace = 0                           # Namespace(s) of articles to list
limit = 500                             # Go by groups of this many articles
out_file_path = ""                      # Where to put the output file

params = {
    "action": "query",
    "list": "categorymembers",
    "cmtitle": "Category:" + category_name,
    "cmnamespace": str(namespace),
    "cmlimit": str(limit),
    "cmcontinue": "0",
    "format": "json",
}

while 1:
    r = requests.get(url=base_url + "/api.php", params=params)
    data = r.json()
    page_list = data['query']['categorymembers']

    with open(out_file_path + category_name + ".txt", "a", encoding="utf-8") as f:
        for p in page_list:
            title = str(p['title'])
            f.write(title + '\n')
            print(title)
    f.close()

    if len(page_list) > 0:
        params['cmcontinue'] = data['continue']['cmcontinue']
    else:
        break