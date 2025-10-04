import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
import re

# Embedded keywords (previously in keywords.json)
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
        "children", "LGBTQ", "queer", "sexuality education", "personal", "protection",
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

priority = ["Governance", "Learning", "Safety", "Climate"]

URL = "https://www.hclfoundation.org/work-with-us"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_hcl():
    listings = []

    try:
        res = requests.get(URL, headers=HEADERS, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Find all rows in the opportunities table
        rows = soup.find_all("tr")
        for row in rows:
            title_td = row.find("td", class_="views-field-field-job-title")
            link_td = row.find("td", class_="views-field-field-download-cta")
            deadline_td = row.find("td", class_="views-field-field-post-date")

            if not title_td or not link_td or not deadline_td:
                continue

            title = title_td.get_text(strip=True)

            a_tag = link_td.find("a", href=True)
            link = None
            if a_tag:
                link = a_tag["href"].strip()
                if not link.startswith("http"):
                    link = "https://www.hclfoundation.org" + link

            deadline_str = deadline_td.get_text(strip=True)

            # Parse deadline into date (if possible)
            deadline = None
            try:
                deadline = datetime.strptime(deadline_str, "%d %b %Y").date()
            except ValueError:
                try:
                    deadline = datetime.strptime(deadline_str, "%d %B, %Y").date()
                except ValueError:
                    pass  # Keep as None if unparsable

            # Calculate Days_Left
            days_left = pd.NA
            if deadline:
                today = date.today()
                delta = deadline - today
                days_left = delta.days if delta.days >= 0 else -1  # Mark expired as -1 for filtering

            # Keyword matching (allow multiple verticals)
            text_blob = title.lower()
            matched_verticals = []
            for vertical in priority:
                for word in keywords.get(vertical, []):
                    if re.search(r'\b' + re.escape(word.lower()) + r'\b', text_blob):
                        matched_verticals.append(vertical)
                        break  # Prevent duplicate entries per vertical

            # Include all listings (remove strict keyword filter to avoid empty results)
            clickable_link = ""
            if link:
                title_escaped = title.replace('"', '""')
                clickable_link = f'=HYPERLINK("{link}","{title_escaped}")'

            listing = {
                "Source": "HCL Foundation",
                "Type": "N/A",
                "Title": title,
                "Description": "",
                "How_to_Apply": "",
                "Matched_Vertical": ", ".join(matched_verticals) if matched_verticals else "N/A",
                "Deadline": deadline if deadline else deadline_str,  # Fallback to str if unparsable
                "Days_Left": days_left,
                "Clickable_Link": clickable_link
            }
            listings.append(listing)

        if not listings:
            print("⚠️ No opportunities found on HCL Foundation site.")
            return pd.DataFrame()

        df = pd.DataFrame(listings)
        return df

    except Exception as e:
        print(f"❌ HCL scraper failed: {e}")
        return pd.DataFrame()