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
from metro import fetch_metro_tenders # ✅ Added Metro import


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
    except Exception as e:
        print(f"❌ HCL scraper failed: {e}")
        hcl_df = pd.DataFrame()
    
    # ✅ Run Metro Rail Tenders
    print("🔍 Running Nagpur Metro Rail scraper...")
    try:
        # Assuming fetch_metro_tenders now returns a DataFrame with all final_columns
        metro_df = fetch_metro_tenders()
        if metro_df.empty:
            print("⚠️ Nagpur Metro Rail returned no data.")
    except Exception as e:
        print(f"❌ Nagpur Metro Rail scraper failed: {e}")
        metro_df = pd.DataFrame()

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
    # ✅ Align Metro schema (though it should already be aligned by the updated metro.py)
    metro_df = metro_df.reindex(columns=final_columns)

    # Force Nasscom Days_Left blank
    if "Days_Left" in nasscom_df.columns:
        nasscom_df["Days_Left"] = pd.NA

    # Merge everything
    combined_df = pd.concat(
        # ✅ Added metro_df to the list of DataFrames to concatenate
        [ngobox_df, devnet_df, nasscom_df, wri_df, hcl_df, metro_df],
        ignore_index=True
    )

    if combined_df.empty:
        print("❌ No data found from any source.")
        return

    # Ensure Clickable_Link cleaned
    if "Clickable_Link" in combined_df.columns:
        # The cleaning logic is kept to handle other scrapers, 
        # but metro_df now includes the HYPERLINK formula
        combined_df["Clickable_Link"] = combined_df.apply(
            lambda row: row["Clickable_Link"]
            if pd.notna(row["Clickable_Link"]) and "HYPERLINK" in str(row["Clickable_Link"])
            else "",
            axis=1,
        )

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
