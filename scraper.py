import json
import os
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_to_discord(title, url, keyword, job_type):
    """Sends to discord"""
    if not WEBHOOK_URL:
        print("missing WEBHOOK_URL in .env")
        return
    
    message = (
        f"Nowa oferta pracy\n"
        f"Stanowisko: {title}\n"
        f"Lokalizacja: {job_type}\n"
        f"Keyword: {keyword}\n"
        f"Link: {url}"
    )

    payload = {"content": message}

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print(f"sent to discord: {title}")
    else:
        print(f"error code {response.status_code}")

BASE_FILE = "seen_offers.json"

if os.path.exists(BASE_FILE):
    with open(BASE_FILE, "r", encoding="utf-8") as file:
        try:
            seen_links = json.load(file)
        except json.JSONDecodeError:
            seen_links = []
else:
    seen_links = []

# keywords for job search
KEYWORDS = [
    "esg",
    "environmental social and governance",
    "zrównoważony rozwój",
    "sustainability",
    "csr",
    "csrd",
    "esrs",
    "corporate social responsibility",
    "raportowanie niefinansowe",
    "non-financial reporting",
    "raportowanie esg",
    "esg reporting",
    "gri",
    "ślad węglowy",
    "carbon footprint",
    "dekarbonizacja",
    "decarbonization",
    "ghg protocol",
    "lca",
    "life cycle assessment",
    "net zero",
    "carbon neutral",
    "ochrona środowiska",
    "environmental protection",
    "gospodarka o obiegu zamkniętym",
    "goz",
    "circular economy",
    "pozwolenia środowiskowe",
    "environmental permits",
    "kobize",
    "bdo",
    "iso 14001",
    "należyta staranność",
    "due diligence",
    "csddd",
    "cs3d",
    "ład korporacyjny",
    "corporate governance",
    "ecovadis",
    "epd",
    "eudr",
    "deforestation"
]

FILTERS = [
    {"type": "Łódź", "link ending": "/lodz;wp"},
    {"type": "remote", "link ending": "?wm=home-office"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for word in KEYWORDS:
    url_encoded_word = quote(word)

    for filter in FILTERS:
        job_type = filter["type"]
        url_ending = filter["link ending"]

        url = f"https://www.pracuj.pl/praca/{url_encoded_word};kw{url_ending}"

        print(f"\n---- Checking: '{word}' | Type: {job_type} ----")
        print(f"URL: {url}")

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"error code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        print("title: ", soup.title.string.strip())

        zero_offers = soup.find(attrs={"data-test":"zero-offers-section"})
        if zero_offers:
            print("zero offers found")
            continue

        links = soup.find_all("a", attrs={"data-test": "link-offer"})
        print(f"found {len(links)} offers")

        for link in links:
            title = link.get("title") or link.text.strip()
            offer_url = link.get("href")

            offer = {
                "title": title,
                "url": offer_url,
                "keyword": word,
                "type": job_type
            }
            if offer_url in seen_links:
                print(f"skipping offer: {title}")
                continue 

            send_to_discord(title, offer_url, word, job_type)
            seen_links.append(offer_url)

            time.sleep(1)

with open(BASE_FILE, "w", encoding="utf-8") as file:
    json.dump(seen_links, file, indent=4, ensure_ascii=False)
