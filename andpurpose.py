import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://andpurpose.world/category/grants/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


# ======================================================
# VERTICAL CLASSIFIER
# ======================================================
def detect_vertical(title):
    t = title.lower()

    if any(x in t for x in ["climate", "environment", "sustainability", "carbon", "energy"]):
        return "Climate"
    elif any(x in t for x in ["women", "girl", "gender", "female", "empowerment"]):
        return "Women & Gender"
    elif any(x in t for x in ["governance", "policy", "democracy", "rights", "public"]):
        return "Governance"
    elif any(x in t for x in ["education", "school", "learning", "training", "scholarship"]):
        return "Education"
    elif any(x in t for x in ["health", "medical", "hospital", "mental", "nutrition"]):
        return "Health"
    elif any(x in t for x in ["agriculture", "farmer", "rural", "livelihood"]):
        return "Agriculture & Rural"
    else:
        return "Other"


# ======================================================
# FETCH LISTINGS
# ======================================================
def fetch_all_cards():
    all_items = []
    seen_links = set()
    page = 1
    MAX_PAGES = 10

    while page <= MAX_PAGES:
        url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
        print(f"🔍 AndPurpose Page {page}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            soup = BeautifulSoup(res.text, "html.parser")
        except:
            break

        articles = soup.find_all("article", class_="masonry-blog-item")

        if not articles:
            break

        for art in articles:
            a_tag = art.find("a", class_="entire-meta-link")
            if not a_tag:
                continue

            link = a_tag.get("href", "").strip()
            if not link or link in seen_links:
                continue

            title_tag = art.find("h3", class_="title")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            all_items.append({"Title": title, "Link": link})
            seen_links.add(link)

        page += 1
        time.sleep(1)

    print(f"✅ AndPurpose Total: {len(all_items)}")
    return all_items


# ======================================================
# DETAIL SCRAPER
# ======================================================
def extract_details(item):
    link = item["Link"]
    title = item["Title"]

    try:
        res = requests.get(link, headers=HEADERS, timeout=10, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
    except:
        return None

    full_text = soup.get_text(" ", strip=True)

    # Description
    paragraphs = soup.find_all("p")
    clean_paras = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
    description = " ".join(clean_paras[:3])

    # How to Apply
    how_to_apply = "N/A"
    for p in paragraphs:
        txt = p.get_text(" ", strip=True).lower()
        if "apply" in txt or "application" in txt:
            how_to_apply = p.get_text(strip=True)
            break

    # Deadline
    deadline = None
    match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', full_text)
    if match:
        deadline = match.group(1)

    # Days Left
    days_left = None
    if deadline:
        try:
            d = pd.to_datetime(deadline, errors='coerce')
            if pd.notna(d):
                today = pd.Timestamp.today().normalize()
                days_left = (d - today).days
        except:
            pass

    # Vertical
    vertical = detect_vertical(title)

    return {
        "Source": "AndPurpose",
        "Type": "Grant",
        "Title": title,
        "Description": description,
        "How_to_Apply": how_to_apply,
        "Matched_Vertical": vertical,
        "Deadline": deadline,
        "Days_Left": days_left,
        "Clickable_Link": link
    }


# ======================================================
# MAIN FUNCTION (IMPORTANT)
# ======================================================
def scrape_andpurpose():
    listings = fetch_all_cards()

    all_data = []

    for i, item in enumerate(listings):
        print(f"🔗 AndPurpose {i+1}/{len(listings)}")

        data = extract_details(item)
        if data:
            all_data.append(data)

        time.sleep(1)

    if not all_data:
        print("⚠️ AndPurpose returned no data.")
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    # Filter valid deadlines
    df["Deadline_Date"] = pd.to_datetime(df["Deadline"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    df = df[df["Deadline_Date"].notna()]
    df = df[df["Deadline_Date"] >= today]

    df = df.sort_values("Deadline_Date")

    print(f"  -> AndPurpose scraped {len(df)} items.")
    return df