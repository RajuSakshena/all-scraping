import time
import re
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dev import load_verticals, match_verticals, format_deadline, compute_days_left

URLS = {
    "Grants": "https://ngobox.org/grant_announcement_listing.php",
    "Tenders": "https://ngobox.org/rfp_eoi_listing.php"
}

# Create Cloudflare bypass scraper
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False
    }
)


def safe_request(url):
    for attempt in range(3):
        try:
            res = scraper.get(url, timeout=25)

            if res.status_code == 200:
                return res

            print(f"⚠️ Response {res.status_code} attempt {attempt+1}")

        except Exception as e:
            print(f"⚠️ Request error attempt {attempt+1}: {e}")

        time.sleep(3)

    return None


def extract_description_after_apply_by(soup):

    h2_tags = soup.find_all('h2', class_='card-text')

    for h2 in h2_tags:

        strong = h2.find('strong')

        if strong and 'Apply By:' in strong.text:

            desc_parts = []

            for sibling in h2.find_all_next():

                if sibling.name == "div" and "row_section" in sibling.get("class", []):
                    break

                text_content = sibling.get_text(separator='\n', strip=True)

                if text_content:
                    desc_parts.append(text_content)

            return "\n".join(desc_parts)

    return ''


def extract_how_to_apply(description):

    if not description:
        return "N/A"

    keywords = [
        "Selection Criteria",
        "Evaluation",
        "Application Guidelines",
        "Eligible Applicants",
        "Scope of Work",
        "Proposal Requirements",
        "Submission Details",
        "How to apply",
        "Eligibility Criteria",
        "Documents Required"
    ]

    norm_keywords = [k.lower() for k in keywords]

    segments = re.split(r'(\.\s+|\n+)', description)

    matched_sections = []

    for seg in segments:

        if any(k in seg.lower() for k in norm_keywords):

            matched_sections.append("• " + seg.strip())

    return "\n".join(matched_sections) if matched_sections else "N/A"


def fetch_opportunities(type_name, base_url, verticals):

    listings = []
    seen_links = set()

    page = 1
    MAX_PAGES = 5

    while page <= MAX_PAGES:

        url = f"{base_url}?page={page}"

        print(f"🔍 Scraping {type_name} Page {page} → {url}")

        res = safe_request(url)

        if not res:
            print("❌ Page request failed")
            break

        soup = BeautifulSoup(res.text, 'html.parser')

        cards = soup.select("div.card-block")

        if not cards:
            print(f"⚠️ No cards found on {type_name} Page {page}. Stopping.")
            break

        for card in cards:

            a = card.find("a", href=True)

            if not a:
                continue

            link = a["href"]

            if not link.startswith("http"):
                link = "https://ngobox.org/" + link.lstrip("/")

            title = a.get_text(strip=True)

            if link in seen_links:
                continue

            detail_res = safe_request(link)

            if not detail_res:
                continue

            detail_soup = BeautifulSoup(detail_res.text, 'html.parser')

            deadline = "N/A"

            for tag in detail_soup.find_all("h2", class_="card-text"):

                strong = tag.find("strong")

                if strong and "Apply By:" in strong.text:
                    deadline = tag.get_text(strip=True).replace("Apply By:", "").strip()
                    break

            description_html = extract_description_after_apply_by(detail_soup)

            description = BeautifulSoup(description_html, "html.parser").get_text(separator=" ", strip=True)

            how_to_apply = extract_how_to_apply(description)

            text_blob = (title + " " + description).lower()

            matched_verticals = match_verticals(text_blob, verticals)

            if not matched_verticals:
                continue

            listings.append({
                "Type": type_name,
                "Title": title,
                "Description": description,
                "How_to_Apply": how_to_apply,
                "Matched_Vertical": ", ".join(sorted(set(matched_verticals))),
                "Deadline": format_deadline(deadline),
                "Days_Left": compute_days_left(deadline),
                "Clickable_Link": f'=HYPERLINK("{link}","{title}")'
            })

            seen_links.add(link)

        page += 1
        time.sleep(2)

    return listings


def scrape_ngobox():

    verticals = load_verticals("keywords.json")

    all_data = []

    for name, url in URLS.items():
        all_data.extend(fetch_opportunities(name, url, verticals))

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    df["Source"] = "NGOBOX"

    if "Type" in df.columns:
        cols = [c for c in df.columns if c != "Type"] + ["Type"]
        df = df[cols]

    return df


if __name__ == "__main__":

    df = scrape_ngobox()

    print(df.head())
