import streamlit as st
import os
import base64
import pandas as pd
from combined_scraper import run_combined_scraper
from datetime import datetime

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(
    page_title="Grants & RFP Scraper",
    layout="wide"
)

# ------------------------------------------------------
# Image Loading
# ------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(APP_DIR, "TMI.png")
logo_base64 = ""
try:
    with open(logo_path, 'rb') as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    pass

# ------------------------------------------------------
# GLOBAL CSS (Including styles from scraper.html)
# ------------------------------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Force white background and remove dark styling */
.stApp {
    background-color: white !important;
    color: #0b3c5d !important;
}
body {
    background-color: white !important;
    font-family: 'Inter', sans-serif !important;
    color: #0b3c5d;
}
.block-container {
    padding-top: 1rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    padding-bottom: 0rem !important;
}

/* Override Streamlit button for download visibility */
div.stDownloadButton > button:first-child {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #fff;
    color: #000 !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: 1px solid #000;
    cursor: pointer;
    transition: 0.3s;
}
div.stDownloadButton > button:first-child:hover {
    background: #000;
    color: #fff !important;
    border: 1px solid #000;
}

/* Custom styling for Run Scraper button */
div.stButton > button:first-child {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #fff;
    color: #000 !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: 1px solid #000;
    cursor: pointer;
    transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background: #fff;
    color: #000 !important;
    border: 1px solid #000;
}

/* Force black text in dataframe cells */
div[data-testid="stDataFrame"] td {
    color: #000 !important;
}

/* Navbar from scraper.html */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5% 0.5rem 5%;
    background: #ffffff;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 15px;
}
.logo-container {
    width: 150px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 5px;
    box-sizing: border-box;
}
.logo-container img {
    max-height: 40px;
    width: auto;
    object-fit: contain;
}

/* Footer from scraper.html */
footer {
    background: #003055;
    color: #cbd5e1;
    padding: 4rem 5% 2rem;
    margin-top: 0;
    margin-bottom: 0;
    font-family: 'Inter', sans-serif;
}
.footer-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1.5fr;
    gap: 2rem;
    margin-bottom: 3rem;
}
.footer-col h4 {
    color: #fff;
    margin-bottom: 1.5rem;
}
.footer-col ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
.footer-col li {
    margin-bottom: 0.75rem;
}
.footer-col a {
    color: #cbd5e1;
    text-decoration: none;
    transition: 0.3s;
}
.footer-col a:hover {
    color: #58a648;
}
.donate-box {
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
}
.footer-bottom {
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 2rem;
    text-align: center;
    font-size: 0.9rem;
}

/* Hero from original app.py */
.hero {
    background: #083a5c;
    text-align: center;
    padding: 60px 10px;
    color: white;
    font-family: 'Inter', sans-serif;
}

/* Content styling to match centered website layout */
.content {
    padding: 4rem 5% 4rem 5%;
    font-family: 'Inter', sans-serif;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}
.content > * {
    margin-bottom: 2rem;
}
.content h1, .content h3, .content p {
    text-align: center;
}
.content .stAlert {
    margin: 0 auto;
    width: fit-content;
}
.content .stDownloadButton {
    display: flex;
    justify-content: center;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# NAVBAR from scraper.html (without buttons)
# ------------------------------------------------------
st.markdown(f"""
<nav class="navbar">
    <div class="logo-container">
        <a href="index.html"><img src="data:image/png;base64,{logo_base64}" alt="TMI Logo"></a>
    </div>
    <div class="nav-right">
    </div>
</nav>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>ImpactStream</h1>
    <p>We find the funding. You do the work.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# CONTENT SECTION
# ------------------------------------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown('<h1 style="text-align: center;">📊 Grants & RFP Combined Scraper</h1>', unsafe_allow_html=True)
    st.markdown("""
This app scrapes **NGOBOX**, **DevNetJobsIndia**, **Nasscom Foundation**, **WRI India**, **HCL Foundation**,
and **Nagpur Metro Rail (New)**,**Niua
**, merges results, categorizes them, and sorts by soonest deadlines (`Days_Left`).
""")
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("🔄 Run Scraper"):
            with st.spinner("Scraping in progress... please wait ⏳"):
                try:
                    run_combined_scraper()
                    st.success("✅ Scraping completed! Data saved to `all_grants.xlsx`.")
                except Exception as e:
                    st.error(f"❌ Scraping failed: {e}")
                    st.info("Please try again or check the logs for details.")

if os.path.exists("all_grants.xlsx"):
    try:
        df = pd.read_excel("all_grants.xlsx")
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
        df["Days_Left"] = pd.to_numeric(df["Days_Left"], errors="coerce")
        df["Days_Left"] = df["Days_Left"].apply(lambda x: int(x) if pd.notna(x) else x)
        st.sidebar.header("Filters")
        verticals = sorted(df["Matched_Vertical"].dropna().unique())
        selected_verticals = st.sidebar.multiselect(
            "Filter by Vertical:",
            options=verticals,
            default=[]
        )
        sources = sorted(df["Source"].dropna().unique())
        selected_sources = st.sidebar.multiselect(
            "Filter by Source:",
            options=sources,
            default=[]
        )
        filtered_df = df.copy()
        if selected_verticals:
            filtered_df = filtered_df[filtered_df["Matched_Vertical"].isin(selected_verticals)]
        if selected_sources:
            filtered_df = filtered_df[filtered_df["Source"].isin(selected_sources)]
        if not (set(selected_sources).issubset({"Nasscom", "WRI"})):
            if not filtered_df["Days_Left"].dropna().empty:
                valid_days = filtered_df["Days_Left"].dropna()
                if not valid_days.empty:
                    min_days = int(valid_days.min()) if not pd.isna(valid_days.min()) else 0
                    max_days = int(valid_days.max()) if not pd.isna(valid_days.max()) else 365
                else:
                    min_days, max_days = 0, 365
                if max_days > 365:
                    max_days = 365
                
                days_range = st.sidebar.slider(
                    "Days Left Range:",
                    min_value=max(min_days, 0),
                    max_value=max_days,
                    value=(0, min(60, max_days)),
                    step=1
                )
                filtered_df = filtered_df[
                    (filtered_df["Days_Left"].fillna(999) >= days_range[0]) &
                    (filtered_df["Days_Left"].fillna(999) <= days_range[1])
                ]
        st.write("### 📊 Breakdown by Source")
        if filtered_df.empty:
            st.warning("⚠️ No data matches the selected filters.")
        else:
            st.write(filtered_df["Source"].value_counts())
            st.write(f"### 📑 Showing {len(filtered_df)} opportunities")
            display_df = filtered_df.drop(columns=["Clickable_Link"], errors="ignore")
            st.dataframe(
                display_df.style.background_gradient(subset=["Days_Left"], cmap="coolwarm", vmin=0, vmax=60),
                use_container_width=True,
                height=600
            )
        col_d1, col_d2, col_d3 = st.columns([1,2,1])
        with col_d2:
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
    col_i1, col_i2, col_i3 = st.columns([1,2,1])
    with col_i2:
        st.info("ℹ️ No data yet. Click **Run Scraper** to generate.")

# ------------------------------------------------------
# FOOTER from scraper.html (without donate button)
# ------------------------------------------------------
st.markdown(f"""
<footer>
    <div class="footer-grid">
        <div class="footer-col">
            <img src="data:image/png;base64,{logo_base64}" style="height:50px; margin-bottom:1rem;">
            <p>The Metropolitan Institute is a think-and-do tank dedicated to building aspirational and resilient regions.</p>
        </div>
        <div class="footer-col">
            <h4>Quick Links</h4>
            <ul>
                <li><a href="about.html">About Us</a></li>
                <li><a href="research.html">Our Research</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>Connect</h4>
            <ul>
                <li><a href="https://x.com/TheMetroInst" target="_blank">Twitter / X</a></li>
                <li><a href="https://www.linkedin.com/company/the-metropolitan-institute" target="_blank">LinkedIn</a></li>
                <li><a href="https://www.instagram.com/themetropolitaninstitute" target="_blank">Instagram</a></li>
            </ul>
        </div>
        <div class="footer-col">
            <div class="donate-box">
                <h4>Support Our Mission</h4>
                <p>Help us bridge the gap between policy and people.</p>
            </div>
        </div>
    </div>
    <div class="footer-bottom">
        © 2025 The Metropolitan Institute. All Rights Reserved.
    </div>
</footer>
""", unsafe_allow_html=True)
