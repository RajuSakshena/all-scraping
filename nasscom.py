import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time  # ✅ Added for retries
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

URL = "https://www.nasscomfoundation.org/requestproposal"

KEYWORDS = {
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
        "skilling", "Upskilling", "Digital", "Technology",
        "Skills & Entrepreneurship", "100 Women Micro Entrepreneurs"
    ],
    "Safety": [
        "gender", "safety", "equity", "mobility", "transport", "sexual", "health",
        "responsive", "institutional safety", "SAFER", "security", "protection",
        "wellbeing", "wellness", "happiness", "access", "accessibility", "child",
        "children", "LGBTQ", "queer", "sexuality education", "personal", "protection",
        "empowerment", "design", "Women in Innovation", "Women Entrepreneurs"
    ],
    "Climate": [
        "climate", "resilience", "environment", "disaster", "sustainability", "green",
        "climate adaptation", "democratize climate", "ecology", "conservation",
        "renewable", "pollution", "energy", "climate mitigation", "green buildings",
        "greening education", "CDRI", "disaster management", "disaster resilience",
        "flood", "heat", "heat islands"
    ]
}

# ✅ Added full headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}

def match_vertical(text: str) -> str:
    text_lower = text.lower()
    for category, words in KEYWORDS.items():
        for word in words:
            if word.lower() in text_lower:
                return category
    return ""

def scrape_nasscom():
    print(f"🔍 Fetching Nasscom page: {URL}")
    response = None
    for attempt in range(3):  # ✅ Add retries (up to 3 attempts)
        try:
            response = requests.get(URL, headers=HEADERS, verify=False, timeout=30)  # ✅ Increased timeout to 30s
            print(f"✅ Nasscom response status: {response.status_code} (Attempt {attempt+1})")
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:  # ✅ Catch specific exceptions
            print(f"⚠️ Nasscom fetch attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)  # Wait before retry
            else:
                if os.path.exists("nasscom.xlsx"):
                    print("📂 Loading fallback nasscom.xlsx")
                    df = pd.read_excel("nasscom.xlsx")
                else:
                    print("⚠️ No fallback file found. Returning empty DF.")
                    return pd.DataFrame()

                # Guarantee schema on fallback
                final_columns = [
                    "Source", "Type", "Title", "Description",
                    "How_to_Apply", "Matched_Vertical", "Deadline",
                    "Days_Left", "Clickable_Link"
                ]
                for col in final_columns:
                    if col not in df.columns:
                        df[col] = pd.NA
                return df[final_columns]

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.pt-3 li strong")

    if not items:
        print("⚠️ No proposal items found on Nasscom page.")
        return pd.DataFrame(columns=[
            "Source", "Type", "Title", "Description",
            "How_to_Apply", "Matched_Vertical", "Deadline",
            "Days_Left", "Clickable_Link"
        ])

    data = []
    for item in items:
        title_text = item.get_text(" ", strip=True)
        link_tag = item.find("a")
        link = f"https://www.nasscomfoundation.org{link_tag['href']}" if link_tag else ""

        matched_vertical = match_vertical(title_text)

        # Only keep items where Matched_Vertical is NOT empty
        if not matched_vertical:
            continue

        clickable = f'=HYPERLINK("{link}","{title_text.replace(chr(34), "”")}")' if link else ""

        data.append({
            "Source": "Nasscom",
            "Type": pd.NA,
            "Title": title_text,
            "Description": pd.NA,
            "How_to_Apply": pd.NA,
            "Matched_Vertical": matched_vertical,
            "Deadline": pd.NaT,
            "Days_Left": pd.NA,
            "Clickable_Link": clickable
        })

    df = pd.DataFrame(data)

    # Guarantee schema
    final_columns = [
        "Source", "Type", "Title", "Description",
        "How_to_Apply", "Matched_Vertical", "Deadline",
        "Days_Left", "Clickable_Link"
    ]
    df = df.reindex(columns=final_columns)

    if not df.empty:
        df.to_excel("nasscom.xlsx", index=False)
        print(f"💾 Saved fallback to nasscom.xlsx (Rows: {len(df)})")

    return df

if __name__ == "__main__":
    print(scrape_nasscom())