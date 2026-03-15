import time
import pandas as pd
from bs4 import BeautifulSoup
import requests

from dev import load_verticals, match_verticals, format_deadline, compute_days_left


URLS = {
    "Grants": "https://ngobox.org/grant_announcement_listing.php",
    "Tenders": "https://ngobox.org/rfp_eoi_listing.php"
}

PROXY = "https://r.jina.ai/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def safe_request(url):

    proxy_url = PROXY + url

    for attempt in range(3):

        try:

            res = requests.get(proxy_url, headers=HEADERS, timeout=30)

            if res.status_code == 200:
                return res

            print(f"⚠️ Response {res.status_code} attempt {attempt+1}")

        except Exception as e:

            print(f"⚠️ Request error attempt {attempt+1}: {e}")

        time.sleep(2)

    print("❌ Page request failed")

    return None


def fetch_opportunities(type_name, base_url, verticals):

    listings = []

    page = 1

    while page <= 5:

        url = f"{base_url}?page={page}"

        print(f"🔍 Scraping {type_name} Page {page} → {url}")

        res = safe_request(url)

        if not res:
            break

        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)

        opp_links = []

        for a in links:

            href = a["href"]

            if "/grant-details/" in href or "/rfp-details/" in href:
                opp_links.append(a)

        if not opp_links:

            print("⚠️ No opportunities found")

            break

        for a in opp_links:

            title = a.get_text(strip=True)

            link = a["href"]

            if not link.startswith("http"):
                link = "https://ngobox.org/" + link.lstrip("/")

            detail = safe_request(link)

            if not detail:
                continue

            dsoup = BeautifulSoup(detail.text, "html.parser")

            deadline = "N/A"

            for h in dsoup.find_all("h2"):

                if "Apply By" in h.text:
                    deadline = h.text.replace("Apply By:", "").strip()
                    break

            text_blob = title.lower()

            matched = match_verticals(text_blob, verticals)

            if not matched:
                continue

            listings.append({
                "Type": type_name,
                "Title": title,
                "Matched_Vertical": ", ".join(matched),
                "Deadline": format_deadline(deadline),
                "Days_Left": compute_days_left(deadline),
                "Clickable_Link": f'=HYPERLINK("{link}","{title}")'
            })

        page += 1

        time.sleep(2)

    return listings


def scrape_ngobox():

    verticals = load_verticals("keywords.json")

    all_data = []

    for name, url in URLS.items():

        data = fetch_opportunities(name, url, verticals)

        all_data.extend(data)

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    df["Source"] = "NGOBOX"

    return df


if __name__ == "__main__":

    df = scrape_ngobox()

    print(df.head())
