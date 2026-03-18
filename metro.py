import requests
import pandas as pd
from bs4 import BeautifulSoup
import json, os, re, string
from datetime import datetime

# === Embedded Keywords Dictionary ===
keywords = {
  "Governance": [
    "governance", "policy", "capacity building", "municipal", "M&E", "fiscal",
    "monitoring and evaluation", "social audits", "fundraising", "management",
    "consulting", "administration", "public", "government", "capacity",
    "impact", "evaluation", "dashboard", "data"
  ],
  "Learning": [
    "education", "skill", "training", "life skills", "TVET", "student",
    "learning by doing", "contextualized learning", "teaching", "development",
    "curriculum", "schools", "colleges", "educational institutes", "AI",
    "skilling"
  ],
  "Safety": [
    "gender", "safety", "equity", "mobility", "transport", "sexual", "health",
    "responsive", "institutional safety", "SAFER", "security", "protection",
    "wellbeing", "wellness", "happiness", "access", "accessibility", "child",
    "children", "LGBTQ", "queer", "sexuality education", "personal","protection",
    "empowerment", "design"
  ],
  "Climate": [
    "climate", "resilience", "environment", "disaster", "sustainability", "green",
    "climate adaptation", "democratize climate", "ecology", "conservation",
    "renewable", "pollution", "energy", "climate mitigation", "green buildings",
    "greening education", "CDRI", "disaster management", "disaster resilience",
    "flood", "heat", "heat islands"
  ]
}
# ==================================

priority = ["Governance", "Learning", "Safety", "Climate"]

BASE_URL = "https://www.metrorailnagpur.com"
URL = f"{BASE_URL}/nagpur-metro-tenders"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_metro_tenders():
    print(f"🔍 Fetching tenders from: {URL}")
    tenders = []
    seen_links = set()

    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        # Updated selector (page uses tables heavily)
        rows = soup.find_all("tr")

        if not rows:
            print("⚠️ No tender rows found.")
            return pd.DataFrame()

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            # Title
            title = cols[1].get_text(strip=True)

            # Find all links
            links = row.find_all("a", href=True)
            if not links:
                continue

            notice_link_tag = None
            for a_tag in links:
                if "notice" in a_tag.get_text(strip=True).lower():
                    notice_link_tag = a_tag
                    break

            if not notice_link_tag:
                notice_link_tag = links[0]

            doc_name = notice_link_tag.get_text(strip=True)
            link = notice_link_tag["href"].strip()

            if not link.startswith("http"):
                link = f"{BASE_URL}/{link.lstrip('/')}"

            if link in seen_links:
                continue
            seen_links.add(link)

            # Keyword matching
            text_blob = title.lower()
            text_blob_clean = text_blob.translate(str.maketrans('', '', string.punctuation))

            matched_verticals = []
            for vertical in priority:
                for word in keywords.get(vertical, []):
                    if re.search(r'\b{}\b'.format(re.escape(word.lower())), text_blob_clean):
                        matched_verticals.append(vertical)
                        break

            if matched_verticals:
                tenders.append({
                    "Title": title,
                    "Description": doc_name,
                    "Matched_Vertical": ", ".join(matched_verticals),
                    "Clickable_Link": '=HYPERLINK("{}","{}")'.format(link, doc_name.replace('"', '""')),
                    "Source": "Nagpur Metro Rail",
                    "Type": "Tender/RFP",
                    "How_to_Apply": f"Refer to the document: {link}",
                    "Deadline": pd.NaT,
                    "Days_Left": pd.NA
                })

        print(f"✅ Found {len(tenders)} tenders.")
        return pd.DataFrame(tenders)

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_metro_tenders()
    print(df.head())
    print(f"Total rows: {len(df)}")
