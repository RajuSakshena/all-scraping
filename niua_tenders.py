import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://niua.in"
TENDERS_URL = "https://niua.in/tenders"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_niua_tenders():
    rows = []
    seen_links = set()

    print("🔍 Scraping NIUA tenders...")

    try:
        response = requests.get(
            TENDERS_URL, headers=HEADERS, timeout=15, verify=False
        )
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"❌ NIUA page load failed: {e}")
        return pd.DataFrame()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        # Only NIUA tender PDFs
        if not href.lower().endswith(".pdf"):
            continue
        if "/sites/default/files/tenders/" not in href:
            continue

        pdf_link = href if href.startswith("http") else BASE_URL + href

        if pdf_link in seen_links:
            continue

        title = a.get_text(strip=True)
        if not title:
            title = pdf_link.split("/")[-1]

        rows.append({
            "Tender_Title": title,
            "Submission_Deadline": pd.NA,
            "Tender_Link": '=HYPERLINK("{}","{}")'.format(
                pdf_link, title.replace('"', '""')
            )
        })

        seen_links.add(pdf_link)

    df = pd.DataFrame(rows)
    print(f"  -> NIUA scraped {len(df)} tenders.")
    return df
