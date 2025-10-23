import streamlit as st
import pandas as pd
from combined_scraper import run_combined_scraper
from datetime import datetime
import os
import re # <-- CRITICAL: Added 're' for regex filtering
# Streamlit page configuration
st.set_page_config(page_title="Grants & RFP Scraper", layout="wide")

# Title and description
st.title("📊 Grants & RFP Combined Scraper")
st.markdown("""
This app scrapes **NGOBOX**, **DevNetJobsIndia**, **Nasscom Foundation**, **WRI India**, **HCL Foundation**, 
and **Nagpur Metro Rail (New)**, merges results, categorizes them, and sorts by soonest deadlines (`Days_Left`).
""")

# Button to trigger scraping
if st.button("🔄 Run Scraper"):
    with st.spinner("Scraping in progress... please wait ⏳"):
        try:
            run_combined_scraper()
            st.success("✅ Scraping completed! Data saved to `all_grants.xlsx`.")
        except Exception as e:
            st.error(f"❌ Scraping failed: {e}")
            st.info("Please try again or check the logs for details.")

# Display data if Excel exists
if os.path.exists("all_grants.xlsx"):
    try:
        df = pd.read_excel("all_grants.xlsx")

        # Ensure Days_Left column exists and is numeric
        if "Days_Left" not in df.columns:
            def compute_days_left(deadline):
                try:
                    dt = pd.to_datetime(deadline, errors="coerce")
                    if pd.isna(dt):
                        return pd.NA
                    return (dt.date() - datetime.today().date()).days
                except:
                    return pd.NA
            df["Days_Left"] = df["Deadline"].apply(compute_days_left)

        # Convert Days_Left to numeric and round to integers
        df["Days_Left"] = pd.to_numeric(df["Days_Left"], errors="coerce")
        df["Days_Left"] = df["Days_Left"].apply(lambda x: int(x) if pd.notna(x) else x)

        # Sidebar filters
        st.sidebar.header("Filters")

        # Vertical filter
        # Extract all unique verticals by splitting comma-separated strings
        all_verticals = df["Matched_Vertical"].dropna().str.split(',\s*').explode().unique()
        verticals = sorted(all_verticals)
        
        selected_verticals = st.sidebar.multiselect(
            "Filter by Vertical:",
            options=verticals,
            default=[]
        )

        # Source filter
        sources = sorted(df["Source"].dropna().unique())
        selected_sources = st.sidebar.multiselect(
            "Filter by Source:",
            options=sources,
            default=[]
        )

        # Apply filters
        filtered_df = df.copy()
        
        if selected_verticals:
            # CRITICAL FIX: Use str.contains with regex for whole-word matching 
            # to handle multi-category entries (like from Metro Rail) correctly.
            search_pattern = r'\b(' + '|'.join(map(re.escape, selected_verticals)) + r')\b'
            filtered_df = filtered_df[
                filtered_df["Matched_Vertical"].astype(str).str.contains(search_pattern, case=False, na=False)
            ]
            
        if selected_sources:
            filtered_df = filtered_df[filtered_df["Source"].isin(selected_sources)]

        # Days Left slider (exclude sources that don't have deadlines if only they are selected)
        # Check if the filtered sources contain only non-deadline sources
        non_deadline_sources = {"Nasscom", "WRI"}
        current_sources = set(filtered_df["Source"].unique())
        
        if not current_sources.issubset(non_deadline_sources):
            # Only proceed with the slider if there's non-empty deadline data in the filtered set
            valid_days = filtered_df["Days_Left"].dropna()
            
            if not valid_days.empty:
                min_days = int(valid_days.min()) if valid_days.min() < 0 else 0
                # Use a maximum of 365 days for the slider range, capping large values
                max_days = int(valid_days.max()) if valid_days.max() < 365 else 365
                max_slider_value = min(365, max_days)
                
                days_range = st.sidebar.slider(
                    "Days Left Range:",
                    min_value=max(min_days, 0),
                    max_value=max_slider_value,
                    value=(0, min(60, max_slider_value)),
                    step=1
                )
                
                # Filter the DataFrame based on the slider range, using a large default (999) for NA values
                filtered_df = filtered_df[
                    (filtered_df["Days_Left"].fillna(999) >= days_range[0]) &
                    (filtered_df["Days_Left"].fillna(999) <= days_range[1])
                ]

        # Display summary
        st.write("### 📊 Breakdown by Source")
        if filtered_df.empty:
            st.warning("⚠️ No data matches the selected filters.")
        else:
            st.write(filtered_df["Source"].value_counts())
            st.write(f"### 📑 Showing {len(filtered_df)} opportunities")

            # Display styled dataframe (hide Clickable_Link for cleaner UI)
            display_df = filtered_df.drop(columns=["Clickable_Link"], errors="ignore")
            st.dataframe(
                display_df.style.background_gradient(subset=["Days_Left"], cmap="coolwarm", vmin=0, vmax=60),
                use_container_width=True,
                height=600
            )

        # Download button
        with open("all_grants.xlsx", "rb") as f:
            st.download_button(
                label="⬇️ Download as Excel",
                data=f,
                file_name="all_grants.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("Please run the scraper again to generate fresh data.")
else:
    st.info("ℹ️ No data yet. Click **Run Scraper** to generate.")
