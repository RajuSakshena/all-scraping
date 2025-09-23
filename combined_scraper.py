import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from datetime import datetime

# Import all three scrapers
from main_scraper import scrape_ngobox
from dev import scrape_devnetjobs
from nasscom import scrape_nasscom
from wri import fetch_wri_opportunities   # ✅ Added WRI import


def run_combined_scraper():
    # Run NGOBOX
    print("🔍 Running NGOBOX scraper...")
    try:
        ngobox_df = scrape_ngobox()
        print(f"✅ NGOBOX scraped {len(ngobox_df)} items")
    except Exception as e:
        print(f"❌ NGOBOX failed: {e}")
        final_columns = [
            "Source", "Type", "Title", "Description",
            "How_to_Apply", "Matched_Vertical", "Deadline",
            "Days_Left", "Clickable_Link"
        ]
        ngobox_df = pd.DataFrame(columns=final_columns)

    # Run DevNetJobs
    print("🔍 Running DevNetJobs India scraper...")
    try:
        devnet_df = scrape_devnetjobs()
        print(f"✅ DevNet scraped {len(devnet_df)} items")
    except Exception as e:
        print(f"❌ DevNet failed: {e}")
        final_columns = [
            "Source", "Type", "Title", "Description",
            "How_to_Apply", "Matched_Vertical", "Deadline",
            "Days_Left", "Clickable_Link"
        ]
        devnet_df = pd.DataFrame(columns=final_columns)
    
    # Run Nasscom
    print("🔍 Running Nasscom scraper...")
    try:
        nasscom_df = scrape_nasscom()
        print(f"✅ Nasscom scraped {len(nasscom_df)} items")
    except Exception as e:
        print(f"❌ Nasscom failed: {e}")
        final_columns = [
            "Source", "Type", "Title", "Description",
            "How_to_Apply", "Matched_Vertical", "Deadline",
            "Days_Left", "Clickable_Link"
        ]
        nasscom_df = pd.DataFrame(columns=final_columns)

    # Run WRI (your existing try-except + add count print)
    print("🔍 Running WRI scraper...")
    try:
        wri_data = fetch_wri_opportunities()
        if wri_data:
            wri_df = pd.DataFrame(wri_data)
            # Add missing schema columns
            wri_df["Source"] = "WRI"
            wri_df["Type"] = "N/A"
            wri_df["Deadline"] = pd.NaT
            wri_df["Days_Left"] = pd.NA
            wri_df = wri_df.rename(columns={"Clickable_Link": "Clickable_Link"}) if "Clickable_Link" in wri_df.columns else wri_df
            print(f"✅ WRI scraped {len(wri_df)} items")
        else:
            wri_df = pd.DataFrame(columns=[
                "Source", "Type", "Title", "Description",
                "How_to_Apply", "Matched_Vertical", "Deadline",
                "Days_Left", "Clickable_Link"
            ])
            print("⚠️ WRI returned no data (0 items).")
    except Exception as e:
        print(f"❌ WRI failed: {e}")
        wri_df = pd.DataFrame(columns=[
            "Source", "Type", "Title", "Description",
            "How_to_Apply", "Matched_Vertical", "Deadline",
            "Days_Left", "Clickable_Link"
        ])
        print("⚠️ WRI failed, using empty DF (0 items)")

    # ✅ Final schema (removed "Link")
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

    # Force Nasscom Days_Left = NaN (blank in Excel)
    if "Days_Left" in nasscom_df.columns:
        nasscom_df["Days_Left"] = pd.NA

    # Merge everything
    combined_df = pd.concat([ngobox_df, devnet_df, nasscom_df, wri_df], ignore_index=True)

    if combined_df.empty:
        print("❌ No data found from any source.")
        return

    # ✅ Ensure Clickable_Link always filled properly
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
        combined_df = combined_df[combined_df["Days_Left"].fillna(0) >= 0]

    # Sort soonest first
    combined_df = combined_df.sort_values(["Days_Left"], ascending=True, na_position="last")

    # Save to Excel
    excel_path = "all_grants.xlsx"
    combined_df.to_excel(excel_path, index=False, engine="openpyxl")

    # Format Excel
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