import os, time, re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dev import load_verticals, match_verticals, parse_deadline, format_deadline, compute_days_left

URLS = {
    "Grants": "https://ngobox.org/grant_announcement_listing.php",
    "Tenders": "https://ngobox.org/rfp_eoi_listing.php"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(HEADERS)

# proxy prefix to bypass 403 on GitHub
PROXY_PREFIX = "https://r.jina.ai/"

def safe_request(url):
    for attempt in range(3):
        try:
            res = session.get(url, timeout=20, verify=False)
            if res.status_code == 200:
                return res
            else:
                print(f"⚠️ Weak response ({res.status_code}) attempt {attempt+1}")
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
            seen_lines = set()
            for sibling in h2.find_all_next():
                if sibling.name == "div" and "row_section" in sibling.get("class", []):
                    b_tag = sibling.find("b")
                    if b_tag and b_tag.get_text(strip=True).lower() == "tags":
                        break
                text_content = sibling.get_text(separator='\n', strip=True)
                lines = text_content.split('\n')
                unique_lines = [line.strip() for line in lines if line.strip() and line.strip() not in seen_lines]
                if unique_lines:
                    seen_lines.update(unique_lines)
                    desc_parts.append('\n'.join(unique_lines))
            return "\n".join(desc_parts)
    return ''


def extract_how_to_apply_from_html(description):

    if not description or not isinstance(description, str):
        return "N/A"

    custom_keywords = [
        "Selection Criteria", "Evaluation & Follow-Up", "Application Guidelines",
        "Eligible Applicants:", "Scope of Work:", "Proposal Requirements",
        "Evaluation Criteria", "Submission Details", "Eligible Entities",
        "How to apply", "Purpose of RFP", "Proposal Guidelines",
        "Eligibility Criteria", "Submission of Tender:", "Technical Bid",
        "Documents Required", "Vendor Qualifications", "To apply"
    ]

    norm_keywords = [kw.lower().rstrip(":") for kw in custom_keywords]

    matched_sections = []

    segments = re.split(r'(\.\s+|\n+)', description)
    segments = [s.strip() for s in segments if s.strip() and not s.strip().startswith('.')]

    i = 0

    while i < len(segments):

        segment = segments[i]
        segment_lower = segment.lower()

        if any(kw in segment_lower for kw in norm_keywords):

            section = ["• " + segment]
            i += 1

            while i < len(segments):

                next_segment = segments[i]
                next_segment_lower = next_segment.lower()

                if any(kw in next_segment_lower for kw in norm_keywords):
                    break

                section.append(next_segment)
                i += 1

            matched_sections.append(" ".join(section))

        else:
            i += 1

    return "\n".join(matched_sections).strip() or "N/A"


def fetch_opportunities(type_name, base_url, verticals):

    listings = []
    seen_links = set()

    page = 1
    MAX_PAGES = 5

    while page <= MAX_PAGES:

        raw_url = f"{base_url}?page={page}"

        # proxy url to bypass 403
        url = PROXY_PREFIX + raw_url

        print(f"🔍 Scraping {type_name} Page {page} → {raw_url}")

        res = safe_request(url)

        if not res:
            print("❌ Page request failed")
            break

        soup = BeautifulSoup(res.text, 'html.parser')

        cards = soup.find_all('div', class_='card-block')

        if not cards:
            print(f"⚠️ No more cards found on {type_name} Page {page}. Stopping.")
            break

        for card in cards:

            a = card.find('a', href=True)

            if not a:
                continue

            href = a['href'].strip()

            link = href if href.startswith('http') else f"https://ngobox.org/{href.lstrip('/')}"

            title = a.get_text(strip=True)

            if link in seen_links:
                continue

            detail_url = PROXY_PREFIX + link

            detail_res = safe_request(detail_url)

            if not detail_res:
                continue

            detail_soup = BeautifulSoup(detail_res.text, 'html.parser')

            deadline = 'N/A'

            for tag in detail_soup.find_all('h2', class_='card-text'):
                strong = tag.find('strong')
                if strong and 'Apply By:' in strong.text:
                    deadline = tag.get_text(strip=True).replace('Apply By:', '').strip()
                    break

            description_html = extract_description_after_apply_by(detail_soup)

            description = BeautifulSoup(description_html, 'html.parser').get_text(separator=' ', strip=True)

            how_to_apply = extract_how_to_apply_from_html(description)

            text_blob = (title + " " + description + " " + how_to_apply).lower()

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
                "Clickable_Link": '=HYPERLINK("{}","{}")'.format(link.replace('"','""'), title.replace('"','""'))
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

    df = df[df['Clickable_Link'].notna() & (df['Clickable_Link'].str.strip() != '')]

    df["Source"] = "NGOBOX"

    if "Type" in df.columns:
        cols = [c for c in df.columns if c != "Type"] + ["Type"]
        df = df[cols]

    return df


if __name__ == "__main__":
    print(scrape_ngobox().head())
