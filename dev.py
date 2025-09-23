import json
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

LISTING_URL = "https://www.devnetjobsindia.org/rfp_assignments.aspx"
DETAIL_URL = "https://www.devnetjobsindia.org/JobDescription.aspx?Job_Id={jobid}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# --------------------------
# Load verticals
# --------------------------
def load_verticals(path="keywords.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("verticals", {})

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def match_verticals(text: str, verticals: dict) -> list:
    t = text.lower()
    matched = []
    for vertical, kws in verticals.items():
        for kw in kws:
            if kw.lower() in t:
                matched.append(vertical)
                break
    return matched

# --------------------------
# Deadline Parser
# --------------------------
def parse_deadline(deadline_str: str):
    if not deadline_str or deadline_str == "N/A":
        return pd.Timestamp.max
    for fmt in ("%d-%b-%Y", "%d %b %Y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(deadline_str.strip(), fmt)
        except ValueError:
            continue
    return pd.Timestamp.max

def format_deadline(deadline_str: str):
    dt = parse_deadline(deadline_str)
    if dt == pd.Timestamp.max:
        return "N/A"
    return dt.strftime("%d-%m-%Y")

def compute_days_left(deadline_str: str) -> int:
    dt = parse_deadline(deadline_str)
    if dt == pd.Timestamp.max:
        return 9999
    return (dt.date() - datetime.today().date()).days

# --------------------------
# ASP.NET helpers
# --------------------------
def get_hidden_fields(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    fields = {}
    for field in ["__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"]:
        tag = soup.select_one(f"#{field}")
        if tag and tag.has_attr("value"):
            fields[field] = tag["value"]
    return fields

def simulate_postback(session: requests.Session, hidden: dict, event_target: str) -> str:
    payload = {"__EVENTTARGET": event_target, "__EVENTARGUMENT": ""}
    payload.update(hidden)
    resp = session.post(
        LISTING_URL, data=payload, headers=HEADERS,
        allow_redirects=True, timeout=30, verify=False
    )

    if "JobDescription.aspx?Job_Id=" in resp.url:
        m = re.search(r"JobDescription\.aspx\?Job_Id=(\d+)", resp.url, re.I)
        if m:
            return DETAIL_URL.format(jobid=m.group(1))

    m = re.search(r"JobDescription\.aspx\?Job_Id=(\d+)", resp.text, re.I)
    if m:
        return DETAIL_URL.format(jobid=m.group(1))

    return ""

# --------------------------
# Extractors
# --------------------------
def fetch_detail_page(session: requests.Session, link: str) -> str:
    if not link:
        return ""
    try:
        resp = session.get(link, headers=HEADERS, timeout=30, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.get_text("\n", strip=True)
    except Exception as e:
        print(f"⚠️ Failed to fetch detail page {link}: {e}")
        return ""

def extract_how_to_apply(full_desc: str) -> str:
    if not full_desc:
        return "N/A"

    custom_keywords = [
        "Selection Criteria", "Evaluation & Follow-Up", "Application Guidelines", "Eligible Applicants:",
        "Scope of Work:", "Proposal Requirements", "Evaluation Criteria", "Submission Details", "Eligible Entities",
        "How to apply", "Purpose of RFP", "Proposal Guidelines", "Eligibility Criteria", "Application must include:",
        "Eligibility", "Submission of Tender:", "Technical Bid-", "Who Can Apply", "Documents Required", "Expectation:",
        "Eligibility Criterion:", "Submission terms:", "Vendor Qualifications", "To apply",
        "To know about the eligibility criteria:", "The agency's specific responsibilities include –",
        "SELCO Foundation will be responsible for:", "Partner Eligibility Criteria", "Proposal Submission Requirements",
        "Proposal Evaluation Criteria", "Eligibility Criteria for CSOs to be part of the programme:", "Pre-Bid Queries:",
        "Response to Pre-Bid Queries:", "Submission of Bid:", "Applicant Profiles:", "What we like to see in grant applications:",
        "Research that is supported by the SVRI must:", "Successful projects are most often:", "Criteria for funding:",
        "Before you begin to write your proposal, consider that IEF prefers to fund:",
        "As you prepare your budget, these are some items that IEF will not fund:", "Organizational Profile",
        "Selection Process", "Proposal Submission Guidelines", "Terms and Conditions", "Security Deposit:",
        "Facilities and Support Offered under the call for proposal:", "Prospective Consultants should demonstrate:", 
        "BID INVITATION", "BID SUBMISSION", "Timeline and Instructions for Submission of Quotation and Password", 
        "Purpose of the RFP", "Tools and Software", 
        "TB Alert India seeks request for propsoal (RFP) from the Agencies for Hiring of an Agency/firm – Youth Engagement for Tuberculosis", 
        "The selected partner will:", "For detailed information, please check the complete version of the RFP attached below. ", 
        "to the email ID", "Job Email ID:", "INTRODUCTION ", "CONTACT DETAILS", "Deliverables and Requirements", 
        "Areas of Accountability", "Expected Duration of Work", "Consultancy Cost: ", "Mode of Payment:", 
        "For any questions or inquiries please contact:"
    ]

    norm_keywords = [kw.lower().rstrip(":") for kw in custom_keywords]
    matched_sections = []

    lines = full_desc.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if any(kw in line.lower() for kw in norm_keywords):
            section = ["• " + line]
            i += 1
            while i < len(lines) and not any(kw in lines[i].lower() for kw in norm_keywords):
                section.append(lines[i].strip())
                i += 1
            matched_sections.append("\n".join([s for s in section if s]))
        else:
            i += 1

    return "\n\n".join(matched_sections).strip() or "N/A"

def extract_rows(html: str):
    soup = BeautifulSoup(html, "html.parser")
    return soup.select("tr.gridRow, tr.gridAltRow")

def build_link_from_logo(row) -> str:
    img = row.select_one("img[src*='joblogos/']")
    if not img or not img.has_attr("src"):
        return ""
    m = re.search(r"joblogos/(\d+)", img["src"])
    if not m:
        return ""
    return DETAIL_URL.format(jobid=m.group(1))

def extract_event_target_from_href(href: str) -> str:
    if not href or "javascript:__doPostBack" not in href:
        return ""
    m = re.search(r"__doPostBack\('([^']+)'", href)
    return m.group(1) if m else ""

def extract_assignments(session: requests.Session, html: str, hidden: dict, verticals: dict):
    results = []
    for row in extract_rows(html):
        a_title = row.select_one("a[id*='lnkJobTitle']")
        title = normalize_text(a_title.get_text(strip=True) if a_title else "")

        org = normalize_text(row.select_one("span[id*='lblJobCo']").get_text(strip=True) if row.select_one("span[id*='lblJobCo']") else "")
        loc_text = normalize_text(row.select_one("span[id*='lblLocation']").get_text(strip=True) if row.select_one("span[id*='lblLocation']") else "")
        location = normalize_text(re.sub(r"^Location:\s*", "", loc_text, flags=re.I))

        deadline_text = normalize_text(row.select_one("span[id*='lblApplyDate']").get_text(strip=True) if row.select_one("span[id*='lblApplyDate']") else "")
        deadline = normalize_text(re.sub(r"^Apply by:\s*", "", deadline_text, flags=re.I))

        base_description = " | ".join([p for p in [org, location] if p])
        matched_verticals = match_verticals(f"{title} {base_description}", verticals)
        if not matched_verticals:
            continue

        link = build_link_from_logo(row)
        if not link and a_title:
            event_target = extract_event_target_from_href(a_title.get("href", ""))
            if event_target:
                link = simulate_postback(session, hidden, event_target)
                time.sleep(0.6)

        if not link:
            continue

        full_desc = fetch_detail_page(session, link)
        description = f"{base_description}\n\n{full_desc}" if full_desc else base_description
        how_to_apply = extract_how_to_apply(full_desc)

        results.append({
            "Title": title,
            "Description": description,
            "How_to_Apply": how_to_apply,
            "Deadline": format_deadline(deadline),
            "Days_Left": compute_days_left(deadline),
            "Matched_Vertical": ", ".join(sorted(set(matched_verticals))),
            "Clickable_Link": '=HYPERLINK("{}","{}")'.format(link.replace('"', '""'), title.replace('"', '""'))
        })
    return results

# --------------------------
# Main
# --------------------------
def scrape_devnetjobs():
    verticals = load_verticals("keywords.json")
    session = requests.Session()
    resp = session.get(LISTING_URL, headers=HEADERS, timeout=30, verify=False)
    resp.raise_for_status()
    hidden = get_hidden_fields(resp.text)
    rows = extract_assignments(session, resp.text, hidden, verticals)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["Source"] = "DevNetJobsIndia"
    df["Type"] = ""
    df = df[["Source", "Type", "Title", "Description", "How_to_Apply",
             "Matched_Vertical", "Deadline", "Days_Left", "Clickable_Link"]]
    return df

if __name__ == "__main__":
    print(scrape_devnetjobs().head())
