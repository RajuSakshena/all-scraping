import streamlit as st
import pandas as pd
from combined_scraper import run_combined_scraper
from datetime import datetime
import os

st.set_page_config(page_title="Grants & RFP Scraper", layout="wide")

st.title("📊 Grants & RFP Combined Scraper")

st.markdown("""
This app scrapes **NGOBOX**, **DevNetJobsIndia**, **Nasscom Foundation**, and **WRI India**,  
merges results, categorizes them, and sorts by soonest deadlines (`Days_Left`).
""")

# Button to trigger scraping
if st.button("🔄 Run Scraper"):
    with st.spinner("Scraping in progress... please wait ⏳"):
        run_combined_scraper()
    st.success("✅ Scraping completed! Data saved to `all_grants.xlsx`.")
    
    # ✅ Add debug summary
    st.subheader("🛠 Debug: Latest Scrape Summary")
    if os.path.exists("all_grants.xlsx"):
        df = pd.read_excel("all_grants.xlsx")
        st.write("### Source Counts")
        st.write(df["Source"].value_counts())
        st.write(f"### Total Rows: {len(df)}")
        st.write("### First 10 Rows Preview")
        st.dataframe(df.head(10))
    else:
        st.warning("No data generated.")

# Display data if Excel already exists
if os.path.exists("all_grants.xlsx"):
    df = pd.read_excel("all_grants.xlsx")

    # This is the new change: check for the Days_Left column and fill 9999 values
    if "Days_Left" in df.columns:
        df["Days_Left"] = df["Days_Left"].fillna("").astype(str)
        df["Days_Left"] = df["Days_Left"].replace("9999.0", "")
        df["Days_Left"] = df["Days_Left"].replace("9999", "")
    else:
        df["Days_Left"] = ""
    
    # Sidebar filters
    st.sidebar.header("Filters")

    verticals = st.sidebar.multiselect(
        "Filter by Vertical:",
        options=sorted(df["Matched_Vertical"].dropna().unique()),
        default=[]
    )

    sources = st.sidebar.multiselect(
        "Filter by Source:",
        options=sorted(df["Source"].unique()),
        default=[]
    )
    
    # Apply filters (only verticals + sources, no days filter)
    filtered_df = df.copy()
    if verticals:
        filtered_df = filtered_df[filtered_df["Matched_Vertical"].isin(verticals)]
    if sources:
        filtered_df = filtered_df[filtered_df["Source"].isin(sources)]

    # ✅ Show row counts by source
    st.write("### 📊 Breakdown by Source (After Filters)")
    st.write(filtered_df["Source"].value_counts())

    st.write(f"### 📑 Showing {len(filtered_df)} opportunities")

    # Show styled dataframe
    # The background_gradient is removed because Days_Left is no longer a number
    st.dataframe(filtered_df, use_container_width=True, height=600)

    # Download button
    st.download_button(
        label="⬇️ Download as Excel",
        data=open("all_grants.xlsx", "rb").read(),
        file_name="all_grants.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("ℹ️ No data yet. Click **Run Scraper** to generate.")
