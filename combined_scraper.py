import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from datetime import datetime

# Import all scrapers
from main_scraper import scrape_ngobox
from dev import scrape_devnetjobs
from nasscom import scrape_nasscom
from wri import fetch_wri_opportunities
from hcl import scrape_hcl  # ✅ Added HCL import


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
            # Add missing schema columns for WRI (if not done in wri.py)
            wri_df["Source"] = "WRI"
            wri_df["Type"] = "N/A"
            wri_df["Deadline"] = pd.NaT
            wri_df["Days_Left"] = pd.NA
            # Ensure Clickable_Link column name is correct (renaming logic kept)
            wri_df = wri_df.rename(columns={"Clickable_Link": "Clickable_Link"}) if "Clickable_Link" in wri_df.columns else wri_df
        else:
            wri_df = pd.DataFrame()
            print("⚠️ WRI returned no data.")
    except Exception as e:
        print(f"❌ WRI scraper failed: {e}")
        wri_df = pd.DataFrame()


    # ✅ Run HCL
    print("🔍 Running HCL Foundation scraper...")
    try:
        hcl_df = scrape_hcl()
        if hcl_df.empty:
            print("⚠️ HCL returned no data.")
    except Exception as e:
        print(f"❌ HCL scraper failed: {e}")
        hcl_df = pd.DataFrame()


    # --- Final Schema Alignment and Merging ---

    final_columns = [
        "Source", "Type", "Title", "Description",
        "How_to_Apply", "Matched_Vertical", "Deadline",
        "Days_Left", "Clickable_Link"
    ]

    # Align schemas for all dataframes
    ngobox_df = ngobox_df.reindex(columns=final_columns)
    devnet_df = devnet_df.reindex(columns=final_columns)
    nasscom_df = nasscom_df.reindex(columns=final_columns)
    wri_df = wri_df.reindex(columns=final_columns)
    hcl_df = hcl_df.reindex(columns=final_columns) # ✅ Align HCL DF

    # Force Nasscom Days_Left = NaN (blank in Excel)
    if "Days_Left" in nasscom_df.columns:
        nasscom_df["Days_Left"] = pd.NA

    # Merge everything
    combined_df = pd.concat(
        [ngobox_df, devnet_df, nasscom_df, wri_df, hcl_df], # ✅ Added hcl_df here
        ignore_index=True
    )

    if combined_df.empty:
        print("❌ No data found from any source.")
        return

    # Ensure Clickable_Link always filled properly (for Excel HYPERLINK function)
    if "Clickable_Link" in combined_df.columns:
        combined_df["Clickable_Link"] = combined_df.apply(
            lambda row: row["Clickable_Link"]
            if pd.notna(row["Clickable_Link"]) and "HYPERLINK" in str(row["Clickable_Link"])
            else "",
            axis=1,
        )

    # Filter out expired deadlines (only where Days_Left is numeric)
    if "Days_Left" in combined_df.columns:
        combined_df["Days_Left"] = pd.to_numeric(combined_df["Days_Left"], errors="coerce")
        # Keep rows where Days_Left is NaN (like Nasscom's blank) OR >= 0
        combined_df = combined_df[combined_df["Days_Left"].fillna(999) >= 0] # Fill NaN with a large number to keep them

    # Sort soonest first
    combined_df = combined_df.sort_values(["Days_Left"], ascending=True, na_position="last")

    # Save to Excel
    excel_path = "all_grants.xlsx"
    combined_df.to_excel(excel_path, index=False, engine="openpyxl")

    # Format Excel (Existing logic preserved)
    wb = load_workbook(excel_path)
    ws = wb.active

    col_widths = {
        "A": 15,  # Source
        "B": 15,  # Type
        "C": 50,  # Title
        "D": 100, # Description
        "E": 60,  # How to Apply
        "F": 25,  # Matched Vertical
        "G": 18,  # Deadline
        "H": 12,  # Days_Left
        "I": 60,  # Clickable Link
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
