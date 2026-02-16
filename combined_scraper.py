import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from datetime import datetime

# Import all scrapers
from main_scraper import scrape_ngobox
from dev import scrape_devnetjobs
from nasscom import scrape_nasscom
from wri import fetch_wri_opportunities
from hcl import scrape_hcl
from metro import fetch_metro_tenders  # CRITICAL: Metro import added

# ✅ NIUA IMPORT ADDED (NO EXISTING IMPORT REMOVED)
from niua_tenders import scrape_niua_tenders


def run_combined_scraper():
    # Run NGOBOX
    print("🔍 Running NGOBOX scraper...")
    ngobox_df = scrape_ngobox()

    # Run DevNetJobs
    print("🔍 Running DevNetJobs India scraper...")
    devnet_df = scrape_devnetjobs()
    
    # Run Nasscom
    print("🔍 Running Nasscom scraper...")
    nasscom_df = scrape_nasscom()

    # Run WRI
    print("🔍 Running WRI scraper...")
    try:
        wri_data = fetch_wri_opportunities()
        if wri_data:
            wri_df = pd.DataFrame(wri_data)
            wri_df["Source"] = "WRI"
            wri_df["Type"] = "N/A"
            wri_df["Deadline"] = pd.NaT
            wri_df["Days_Left"] = pd.NA
            wri_df = wri_df.rename(columns={"Clickable_Link": "Clickable_Link"}) if "Clickable_Link" in wri_df.columns else wri_df
            print(f"  -> WRI scraped {len(wri_df)} items.")
        else:
            wri_df = pd.DataFrame()
            print("⚠️ WRI returned no data.")
    except Exception as e:
        print(f"❌ WRI scraper failed: {e}")
        wri_df = pd.DataFrame()

    # Run HCL
    print("🔍 Running HCL Foundation scraper...")
    try:
        hcl_df = scrape_hcl()
        if hcl_df.empty:
            print("⚠️ HCL returned no data.")
        else:
            print(f"  -> HCL scraped {len(hcl_df)} items.")
    except Exception as e:
        print(f"❌ HCL scraper failed: {e}")
        hcl_df = pd.DataFrame()
    
    # Run Metro Rail Tenders
    print("🔍 Running Nagpur Metro Rail scraper...")
    try:
        metro_df = fetch_metro_tenders()
        if metro_df.empty:
            print("⚠️ Nagpur Metro Rail returned no data.")
        else:
            print(f"  -> Nagpur Metro Rail scraped {len(metro_df)} items.")
    except Exception as e:
        print(f"❌ Nagpur Metro Rail scraper failed: {e}")
        metro_df = pd.DataFrame()

    # ✅ RUN NIUA SCRAPER (ADDED, NOTHING REMOVED)
    print("🔍 Running NIUA Tenders scraper...")
    try:
        niua_raw_df = scrape_niua_tenders()
        if niua_raw_df.empty:
            print("⚠️ NIUA returned no data.")
            niua_df = pd.DataFrame()
        else:
            print(f"  -> NIUA scraped {len(niua_raw_df)} items.")
            niua_df = pd.DataFrame({
                "Source": "NIUA",
                "Type": "Tender",
                "Title": niua_raw_df["Tender_Title"],
                "Description": pd.NA,
                "How_to_Apply": pd.NA,
                "Matched_Vertical": pd.NA,
                "Deadline": niua_raw_df["Submission_Deadline"],
                "Days_Left": pd.NA,
                "Clickable_Link": niua_raw_df["Tender_Link"]
            })
    except Exception as e:
        print(f"❌ NIUA scraper failed: {e}")
        niua_df = pd.DataFrame()

    # --- Final Schema Alignment and Merging ---
    final_columns = [
        "Source", "Type", "Title", "Description",
        "How_to_Apply", "Matched_Vertical", "Deadline",
        "Days_Left", "Clickable_Link"
    ]

    # Align schemas
    ngobox_df = ngobox_df.reindex(columns=final_columns)
    devnet_df = devnet_df.reindex(columns=final_columns)
    nasscom_df = nasscom_df.reindex(columns=final_columns)
    wri_df = wri_df.reindex(columns=final_columns)
    hcl_df = hcl_df.reindex(columns=final_columns)
    metro_df = metro_df.reindex(columns=final_columns)  # Align Metro schema
    niua_df = niua_df.reindex(columns=final_columns)    # ✅ NIUA ALIGNMENT ADDED

    # Force Nasscom Days_Left blank
    if "Days_Left" in nasscom_df.columns:
        nasscom_df["Days_Left"] = pd.NA

    # Merge everything, INCLUDING metro_df AND niua_df
    combined_df = pd.concat(
        [ngobox_df, devnet_df, nasscom_df, wri_df, hcl_df, metro_df, niua_df],
        ignore_index=True
    )

    if combined_df.empty:
        print("❌ No data found from any source.")
        return

    # 🔥 SENIOR-LEVEL UX & DATA QUALITY FIXES (Description Truncation + Clean Clickable_Link)
    # These are the ONLY changes - everything else is untouched

    # 1. Clean Clickable_Link: Extract pure URL from Excel HYPERLINK formula
    def clean_clickable_link(link):
        if pd.isna(link) or str(link).strip() == "":
            return ""
        link_str = str(link).strip()
        # Detect HYPERLINK formula and safely extract URL
        if link_str.upper().startswith("=HYPERLINK"):
            try:
                start_idx = link_str.find('"') + 1
                if start_idx > 0:
                    end_idx = link_str.find('"', start_idx)
                    if end_idx > start_idx:
                        return link_str[start_idx:end_idx]
            except Exception:
                pass  # Safe fallback
        return link_str

    combined_df["Clickable_Link"] = combined_df["Clickable_Link"].apply(clean_clickable_link)

    # 2. Truncate Description for Excel UX (300 chars + " ... Read More")
    def truncate_description(desc):
        if pd.isna(desc) or str(desc).strip() == "":
            return ""
        desc_str = str(desc).strip()
        if len(desc_str) > 300:
            # Truncate cleanly and append suffix
            return desc_str[:300].rstrip() + " ... Read More"
        return desc_str

    combined_df["Description"] = combined_df["Description"].apply(truncate_description)

    # Filter out expired deadlines
    if "Days_Left" in combined_df.columns:
        combined_df["Days_Left"] = pd.to_numeric(combined_df["Days_Left"], errors="coerce")
        combined_df = combined_df[combined_df["Days_Left"].fillna(999) >= 0]

    # Sort soonest first
    combined_df = combined_df.sort_values(["Days_Left"], ascending=True, na_position="last")

    # Round Days_Left for Excel display (no decimals)
    if "Days_Left" in combined_df.columns:
        combined_df["Days_Left"] = combined_df["Days_Left"].apply(
            lambda x: int(round(x)) if pd.notna(x) else x
        )

    # Save to Excel
    excel_path = "all_grants.xlsx"
    combined_df.to_excel(excel_path, index=False, engine="openpyxl")

    # Format Excel
    wb = load_workbook(excel_path)
    ws = wb.active

    col_widths = {
        "A": 15,
        "B": 15,
        "C": 50,
        "D": 100,
        "E": 60,
        "F": 25,
        "G": 18,
        "H": 12,
        "I": 60,
    }

    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            if cell.column_letter in ["D", "E"]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            else:
                cell.alignment = Alignment(wrap_text=False, vertical="top")

    wb.save(excel_path)

    # Print summary
    print("\n📊 Summary of scraped data:")
    print(combined_df["Source"].value_counts())
    print(f"Total rows in final dataset: {len(combined_df)}")
    print(f"✅ Combined Excel saved as {excel_path} (Rows: {len(combined_df)})")


if __name__ == "__main__":
    run_combined_scraper()
