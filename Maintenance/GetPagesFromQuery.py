import requests

# Grabs a list of page names from a specified query page on the wiki

base_url = "" 
query_page = "Unusedimages" # e.g. "Unusedimages" or "Unusedcategories"
out_file_path = ""          # Where to save the output file
offset = 0                  # Start from this number on the list
limit = 100                 # Proceed in groups of pages this big

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
