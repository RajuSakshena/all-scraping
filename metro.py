import requests
import pandas as pd
from bs4 import BeautifulSoup
import json, os, re, string
from openpyxl import load_workbook
from openpyxl.styles import Alignment
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
    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        seen_links = set()

        # Targeting the table data cells that contain the tender info
        blocks = soup.find_all("td", class_="numeric")
        if not blocks:
            print("⚠️ No tender blocks found.")
            return pd.DataFrame() # Return empty DataFrame on failure

        for block in blocks:
            # Tender title
            header_span = block.find("span", style=lambda s: s and "display:table-cell" in s)
            tender_title = header_span.get_text(strip=True) if header_span else "N/A"

            # Full description
            desc_parts = []
            for element in block.contents:
                if element.name == "table":
                    break
                if isinstance(element, str):
                    text = element.strip()
                else:
                    text = element.get_text(strip=True, separator=" ")
                if text:
                    desc_parts.append(text)
            full_description = " ".join(desc_parts).strip()
            tender_full_title = f"{tender_title} — {full_description}"

            # Inner table with links
            inner_table = block.find("table")
            if not inner_table:
                continue

            for a_tag in inner_table.find_all("a", href=True):
                doc_name = a_tag.get_text(strip=True)
                link = a_tag["href"].strip()
                if link and not link.startswith("http"):
                    link = f"{BASE_URL}/{link.lstrip('/')}"
                if link in seen_links:
                    continue
                seen_links.add(link)

                # Strict keyword matching
                text_blob = full_description.lower()
                text_blob_clean = text_blob.translate(str.maketrans('', '', string.punctuation))
                matched_verticals = []

                for vertical in priority:
                    for word in keywords.get(vertical, []):
                        word_lower = word.lower()
                        if re.search(r'\b{}\b'.format(re.escape(word_lower)), text_blob_clean):
                            matched_verticals.append(vertical)
                            break
                
                # Only include tenders with at least one matched vertical
                if matched_verticals:
                    tenders.append({
                        # --- Columns from original scraper ---
                        "Title": tender_full_title,
                        "Description": doc_name,
                        "Matched_Vertical": ", ".join(matched_verticals),
                        "Clickable_Link": '=HYPERLINK("{}","{}")'.format(link, doc_name.replace('"', '""')),
                        
                        # --- Columns for combined_scraper alignment (set to default/null) ---
                        "Source": "Nagpur Metro Rail",
                        "Type": "Tender/RFP",
                        "How_to_Apply": f"Refer to the documents linked: {link}",
                        "Deadline": pd.NaT, # Not available, use pandas NaT (Not a Time)
                        "Days_Left": pd.NA # Not available, use pandas NA (Not Applicable)
                    })

        print(f"✅ Found {len(tenders)} matched tender documents.")
        
        # Convert to DataFrame
        df = pd.DataFrame(tenders)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network or request error during scraping: {e}")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# The save_to_excel function is removed as combined_scraper.py handles saving.
if __name__ == "__main__":
    # Test the function, will now return a DataFrame
    data_df = fetch_metro_tenders()
    print(data_df.head()) # Print a preview of the structured data
    print(f"Total rows: {len(data_df)}")
