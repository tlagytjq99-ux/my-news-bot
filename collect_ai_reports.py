import requests
from bs4 import BeautifulSoup
import time
import re

BASE_URL = "https://www.oecd.org"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def is_ai_related(text):
    text = text.lower()
    return any(k.lower() in text for k in AI_KEYWORDS)

res = requests.get(f"{BASE_URL}/publications/", headers=HEADERS)
soup = BeautifulSoup(res.text, "html.parser")

reports = []

for item in soup.select("a"):
    title = item.get_text(strip=True)
    link = item.get("href")

    if title and link and is_ai_related(title):
        reports.append({
            "title": title,
            "url": link if link.startswith("http") else BASE_URL + link,
            "source": "OECD"
        })
        time.sleep(1)
