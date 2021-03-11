import requests
import lxml
import bs4
from selenium import webdriver

FILE_URL_BASE = "https://starwars.fandom.com/wiki/"

USERNAME = "YOUR_FANDOM_USERNAME"
PASSWORD = "YOUR_FANDOM_PASSWORD"

filenames = []

# Log in to your Fandom account.
def auto_login(d, username, password):
    d.get("https://www.fandom.com/signin")
    uname = d.find_element_by_id("loginUsername")
    uname.click()
    uname.send_keys(username)
    pswrd = d.find_element_by_id("loginPassword")
    pswrd.click()
    pswrd.send_keys(password)
    d.find_element_by_id("loginSubmit").click()
    x = input("Waiting for captcha...")
    print("Success!")

# Download the image at the given filename
def download_file(filename):
    url_string = FILE_URL_BASE + filename                   # This is the full url of the file page on the wiki
    driver.get(url_string)                                  # Send Selenium to that URL
    source = driver.page_source                             # Read the page's HTML
    soup = bs4.BeautifulSoup(source, "lxml")                # Parse the HTML with BeautifulSoup
    url = soup.find(property="og:image")["content"]         # Get the URL of the original file in the wiki database
    r = requests.get(url)                                   # Get the image (NOTE: We don't use Selenium for this!)
    print(filename)
    filename = filename.replace('"', '_')                   # Replace characters that can't be in the filename
    filename = filename.replace('?', '_')
    with open("Files/" + filename[5:], "wb") as f:          # Write the image to a file with the same filename
        f.write(r.content)
    f.close()

# Identify the files we want to download
with open("Filenames.txt", "r", encoding="utf-8") as f:
    filenames = f.read().splitlines()
f.close()

driver = webdriver.Chrome("C:\Program Files (x86)\Google\chromedriver.exe")
auto_login(driver, USERNAME, PASSWORD)

for item in filenames:
    download_file(item)
