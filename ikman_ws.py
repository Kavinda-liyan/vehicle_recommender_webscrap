from bs4 import BeautifulSoup
import requests

ikman_html_text = requests.get(
    "https://ikman.lk/en/ads/sri-lanka/cars?enum.fuel_type=petrol"
)
soup = BeautifulSoup(ikman_html_text.text, "lxml")
vehicle_cards = soup.find_all("li", class_="normal--2QYVk gtm-normal-ad")
for card in vehicle_cards:
    vehicle_title = card.find("h2", class_="heading--2eONR heading-2--1OnX8 title--3yncE block--3v-Ow").text
    vehicle_price = card.find("div", class_="price--3SnqI color--t0tGX").text
    vehicle_location = card.find("div", class_="description--2-ez3").text

    print(f"Title:{vehicle_title}")
    print(f"Price:{vehicle_price}")
    print(f"Location:{vehicle_location}\n")
