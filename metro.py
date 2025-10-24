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
URL = f"{BASE_URL}/tenders"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_metro_tenders():
    print(f"🔍 Fetching tenders from: {URL}")
    tenders = []
    seen_links = set()

    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        blocks = soup.find_all("td", class_="numeric")
        if not blocks:
            print("⚠️ No tender blocks found.")
            return pd.DataFrame()

        for block in blocks:
            header_span = block.find("span", style=lambda s: s and "display:table-cell" in s)
            tender_title = header_span.get_text(strip=True) if header_span else "N/A"

            desc_parts = []
            for element in block.contents:
                if element.name == "table":
                    break
                text = element.get_text(strip=True, separator=" ") if hasattr(element, "get_text") else element.strip()
                if text:
                    desc_parts.append(text)
            full_description = " ".join(desc_parts).strip()
            tender_full_title = f"{tender_title} — {full_description}"

            inner_table = block.find("table")
            if not inner_table:
                continue

            # --- Find all links ---
            all_links = inner_table.find_all("a", href=True)
            if not all_links:
                continue

            # --- Prioritize Notice Inviting link ---
            notice_link_tag = None
            for a_tag in all_links:
                if "notice inviting" in a_tag.get_text(strip=True).lower():
                    notice_link_tag = a_tag
                    break
            if not notice_link_tag:
                notice_link_tag = all_links[0]  # fallback to first link

            doc_name = notice_link_tag.get_text(strip=True)
            link = notice_link_tag["href"].strip()
            if link and not link.startswith("http"):
                link = f"{BASE_URL}/{link.lstrip('/')}"

            if link in seen_links:
                continue
            seen_links.add(link)

            # Keyword matching
            text_blob = full_description.lower()
            text_blob_clean = text_blob.translate(str.maketrans('', '', string.punctuation))
            matched_verticals = []

            for vertical in priority:
                for word in keywords.get(vertical, []):
                    if re.search(r'\b{}\b'.format(re.escape(word.lower())), text_blob_clean):
                        matched_verticals.append(vertical)
                        break

            if matched_verticals:
                tenders.append({
                    "Title": tender_full_title,
                    "Description": doc_name,
                    "Matched_Vertical": ", ".join(matched_verticals),
                    "Clickable_Link": '=HYPERLINK("{}","{}")'.format(link, doc_name.replace('"', '""')),
                    "Source": "Nagpur Metro Rail",
                    "Type": "Tender/RFP",
                    "How_to_Apply": f"Refer to the document: {link}",
                    "Deadline": pd.NaT,
                    "Days_Left": pd.NA
                })

        print(f"✅ Found {len(tenders)} tenders with valid Notice Inviting links.")
        return pd.DataFrame(tenders)

    except requests.exceptions.RequestException as e:
        print(f"❌ Network or request error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_metro_tenders()
    print(df.head())
    print(f"Total rows: {len(df)}")
