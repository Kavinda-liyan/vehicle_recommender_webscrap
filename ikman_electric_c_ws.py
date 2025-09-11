from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re

two_word_manufacturers = ["Mercedes Benz", "Land Rover", "Maruti Suzuki","Mini Cooper"]
noise_words = [
    "Petrol","petrol", "Diesel", "Hybrid", "Electric", 
    "First", "Owner", "Registered", "Unregistered", 
    "Auto", "Manual", "Turbo", "Coupe", "SUV"
]

def parse_vehicle_title(title):
    if not title:
        return {"Manufacturer": None, "Model": None, "Year": None, "Condition": None}

    words = title.split()
    year = None
    condition = None

    #Year
    if re.match(r"^\d{4}$", words[-1]):
        year = words[-1]
        words = words[:-1]

    #condition 
    condition_keywords = ["new", "brandnew", "unregistered","B/New","Brand New","B-New"]
    if words and words[-1].lower() in condition_keywords:
        condition = words[-1]  # keep original case
        words = words[:-1]

    manufacturer = words[0]
    if len(words) > 1:
        first_two = f"{words[0]} {words[1]}"
        if first_two.lower() in [m.lower() for m in two_word_manufacturers]:
            # Match with the original casing from our list
            manufacturer = next(m for m in two_word_manufacturers if m.lower() == first_two.lower())
            words = words[2:]
        else:
            words = words[1:]
    else:
        words = words[1:]

    #remove noise
    clean_words = [w for w in words if w.lower() not in [n.lower() for n in noise_words]]
    model = " ".join(clean_words) if clean_words else None

    return {"Manufacturer": manufacturer, "Model": model, "Year": year, "Condition": condition,"Fuel Type":"Electric"}


#Web Scraper
base_url = "https://ikman.lk/en/ads/sri-lanka/cars?enum.fuel_type=electric"
page = 1
electric_vehicles = []

while True:
    url = f"{base_url}&page={page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    listings = soup.find_all("li", class_="normal--2QYVk gtm-normal-ad")
    if not listings:
        break

    for item in listings:
        title_tag = item.find("h2", class_="heading--2eONR heading-2--1OnX8 title--3yncE block--3v-Ow")
        title = title_tag.text.strip() if title_tag else None

        price_tag = item.find("div", class_="price--3SnqI")
        price = price_tag.text.strip() if price_tag else None

       
        parsed = parse_vehicle_title(title)
        parsed["Price"] = price

        electric_vehicles.append(parsed)
        print(parsed)

    print(f"Scraped page {page}\n")
    page += 1
    time.sleep(2)
    if page > 1000: 
        break

print(f"Total electric vehicles found: {len(electric_vehicles)}")

# Save results to CSV
df = pd.DataFrame(electric_vehicles)

df.drop_duplicates(subset=["Manufacturer", "Model", "Year"], inplace=True)

df.reset_index(drop=True, inplace=True)
df.to_csv("electric_vehicles_c.csv", index=False)
print(f"Cleaned data saved to electric_vehicles.csv with {len(df)} unique vehicles")
