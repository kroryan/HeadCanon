# Grabs a list of page names from a specified query page on the wiki

import requests

base_url = "http://192.168.1.20:1138"   # Base URL of the wiki
query_page = "Unusedimages"             # e.g. "Unusedimages" or "Unusedcategories"
out_file_path = ""                      # Where to put the output file
offset = 0                              # Start from this page on the list
limit = 500                             # Go by groups of this many pages

params = {
    "qplimit": str(limit),
    "qpoffset": str(offset),
    "action": "query",
    "qppage": query_page,
    "list": "querypage",
    "format": "json"
}

while 1:
    params["qpoffset"] = str(offset)
    params["qplimit"] = str(limit)
    r = requests.get(url=base_url + "/api.php", params=params)
    data = r.json()
    querypage = data['query']['querypage']['results']
    with open(out_file_path + query_page + ".txt", "a") as f:
        for p in querypage:
            title = str(p['title'])
            f.write(title + '\n')
            print(title)

        if len(querypage) == 0:
            break
        else:
            offset += limit
    
    f.close()
