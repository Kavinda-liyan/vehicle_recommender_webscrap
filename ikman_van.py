from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import random

two_word_manufacturers = ["Mercedes Benz", "Land Rover", "Maruti Suzuki", "Mini Cooper"]
noise_words = [
    "Petrol", "petrol", "Diesel", "Hybrid", "Electric",
    "First", "Owner", "Registered", "Unregistered",
    "Auto", "Manual", "Turbo", "Coupe", "SUV"
]

def clean_price(price):
    if not price:
        return None
    match = re.search(r"[\d,]+", price)
    if match:
        return int(match.group().replace(",", ""))
    return None

def clean_mileage(mileage):
    if not mileage:
        return None
    match = re.search(r"[\d,]+", mileage)
    if match:
        return int(match.group().replace(",", ""))
    return None

def parse_vehicle_title(title):
    if not title:
        return {"Manufacturer": None, "Model": None, "Year": None, "Condition": None}

    words = title.split()
    year = None
    condition = None

    # Year
    if re.match(r"^\d{4}$", words[-1]):
        year = words[-1]
        words = words[:-1]

    # Condition
    condition_keywords = [
        "new", "brandnew", "unregistered", "B/New", "Brand New", "B-New",
        "used", "secondhand", "second hand", "2nd hand", "2nd owner", "2nd Owner"
    ]
    if words and words[-1].lower() in [c.lower() for c in condition_keywords]:
        condition = words[-1]
        words = words[:-1]

    manufacturer = words[0]
    if len(words) > 1:
        first_two = f"{words[0]} {words[1]}"
        if first_two.lower() in [m.lower() for m in two_word_manufacturers]:
            manufacturer = next(m for m in two_word_manufacturers if m.lower() == first_two.lower())
            words = words[2:]
        else:
            words = words[1:]
    else:
        words = words[1:]

    # Remove noise
    clean_words = [w for w in words if w.lower() not in [n.lower() for n in noise_words]]
    model = " ".join(clean_words) if clean_words else None

    return {"Manufacturer": manufacturer, "Model": model, "Year": year, "Condition": condition, "Fuel Type": "none"}


# --- Web Scraper ---
base_url = "https://ikman.lk/en/ads/sri-lanka/vans"
page = 1
vans = []

headers = {"User-Agent": "Mozilla/5.0"}

while True:
    url = f"{base_url}?page={page}"
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")

    # ⚠️ You may need to update this selector if it still returns nothing
    listings = soup.find_all("li", class_="normal--2QYVk gtm-normal-ad")

    if not listings:
        print("No listings found on this page.")
        break

    for item in listings:
        title_tag = item.find("h2")
        title = title_tag.text.strip() if title_tag else None

        price_tag = item.find("div", class_="price--3SnqI")
        price = clean_price(price_tag.text.strip()) if price_tag else None

        mileage_tag = item.find("div", class_="details--1GUIn")
        if mileage_tag:
            match = re.search(r"([\d,]+)\s*km", mileage_tag.text)
            mileage = clean_mileage(match.group(1)) if match else None
        else:
            mileage = None

        parsed = parse_vehicle_title(title)
        parsed["Price"] = price
        parsed["Mileage"] = mileage

        vans.append(parsed)
        print(parsed)

    print(f"Scraped page {page}\n")
    page += 1
    time.sleep(random.uniform(1.5, 3.5))  # safer delay
    if page > 50:  # safeguard against infinite loops
        break

print(f"Total vans found: {len(vans)}")

# --- CSV Export ---
df = pd.DataFrame(vans)

if df.empty:
    print("⚠️ No data scraped. Check if the selectors are outdated.")
else:
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df[df["Year"] >= 2000]
    df = df.sort_values(by=["Manufacturer", "Year", "Model"], ascending=[True, False, True])

    # Mileage Ranges
    mileage_ranges = {
        "0-20k km": (0, 20000),
        "20k-50k km": (20000, 50000),
        "50k-100k km": (50000, 100000),
        "100k+ km": (100000, float('inf'))
    }

    for label, (min_m, max_m) in mileage_ranges.items():
        df_range = df[(df["Mileage"] >= min_m) & (df["Mileage"] <= max_m)]
        avg_prices = df_range.groupby(["Manufacturer", "Model"])["Price"].mean().reset_index()
        avg_prices[f"Average Price ({label})"] = avg_prices["Price"].round(0).astype('Int64')
        avg_prices.drop(columns=["Price"], inplace=True)
        df = df.merge(avg_prices, on=["Manufacturer", "Model"], how="left")

    df.drop_duplicates(subset=["Manufacturer", "Model", "Year"], inplace=True)
    df = df.sort_values(by=["Manufacturer", "Year", "Model"], ascending=[True, False, True])

    df.reset_index(drop=True, inplace=True)
    df.to_csv("./datasets/vans.csv", index=False)
    print(f"✅ Cleaned data saved to vans.csv with {len(df)} unique vehicles")
