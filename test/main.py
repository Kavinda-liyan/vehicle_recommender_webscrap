from bs4 import BeautifulSoup

with open("index.html", "r", encoding="utf-8") as html_file:
    content = html_file.read()
    soup = BeautifulSoup(content, "lxml")
    product_cards = soup.find_all("div", class_="product")
    for card in product_cards:
        product_title = card.find("h2", class_="title").text
        product_description = card.find("p", class_="desc").text
        product_price = card.find("span", class_="price").text

        print(f"Title:{product_title}")
        print(f"Description:{product_description}")
        print(f"Price:{product_price}\n")
