from bs4 import BeautifulSoup

with open("index.html", "r", encoding="utf-8") as html_file:
    content = html_file.read()
    soup = BeautifulSoup(content, "lxml")
    desc_tags = soup.find_all("p")
    for tag in desc_tags:
        print(tag.get_text())
    
