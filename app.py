import streamlit as st
import pandas as pd
from combined_scraper import run_combined_scraper
from datetime import datetime
import os
import base64

# ------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------
st.set_page_config(page_title="ImpactStream - Grants Scraper", layout="wide")

# ------------------------------------------------------
# Logo Loading
# ------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(APP_DIR, "TMI.png")
logo_base64 = ""

try:
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except:
    pass

# ------------------------------------------------------
# GLOBAL CSS
# ------------------------------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
.stApp { background-color: white !important; font-family: 'Inter', sans-serif; }

.block-container {
    padding-top: 1rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
}

.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:0.8rem 5%;
    background:white;
}

.logo-container {
    width:150px;
    height:50px;
    display:flex;
    align-items:center;
    justify-content:center;
    border:1px solid #e0e0e0;
    border-radius:4px;
    background:white;
}

.logo-container img {
    max-height:40px;
    object-fit:contain;
}

.hero {
    background:#083a5c;
    text-align:center;
    padding:60px 10px;
    color:white;
}

footer {
    background:#003055;
    color:#cbd5e1;
    padding:4rem 5% 2rem;
    margin-top:4rem;
}

.footer-grid {
    display:grid;
    grid-template-columns:1.5fr 1fr 1fr 1.5fr;
    gap:2rem;
    margin-bottom:3rem;
}

.footer-col h4 { color:white; }
.footer-col a { color:#cbd5e1; text-decoration:none; }
.footer-col a:hover { color:#58a648; }

.footer-bottom {
    border-top:1px solid rgba(255,255,255,0.1);
    padding-top:2rem;
    text-align:center;
    font-size:0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# NAVBAR
# ------------------------------------------------------
st.markdown(f"""
<nav class="navbar">
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}">
    </div>
</nav>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# HERO
# ------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>ImpactStream</h1>
    <p>We find the funding. You do the work.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# CENTER CONTENT
# ------------------------------------------------------
col1, col2, col3 = st.columns([1,2,1])

with col2:

    st.markdown("<h1 style='text-align:center;'>📊 Grants & RFP Combined Scraper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Scrapes NGOBOX, DevNetJobsIndia, Nasscom Foundation, WRI India, HCL Foundation, Nagpur Metro Rail, NIUA and more.</p>", unsafe_allow_html=True)

    # Run Scraper Button
    if st.button("🔄 Run Scraper"):
        with st.spinner("Scraping in progress..."):
            try:
                run_combined_scraper()
                st.success("✅ Scraping completed! Data saved to all_grants.xlsx")
            except Exception as e:
                st.error(f"❌ Scraping failed: {e}")

    # Display Data
    if os.path.exists("all_grants.xlsx"):

        df = pd.read_excel("all_grants.xlsx")

        if "Days_Left" not in df.columns:
            def compute_days_left(deadline):
                try:
                    dt = pd.to_datetime(deadline, errors="coerce")
                    if pd.isna(dt): return None
                    return (dt.date() - datetime.today().date()).days
                except:
                    return None

            df["Days_Left"] = df["Deadline"].apply(compute_days_left)

        df["Days_Left"] = pd.to_numeric(df["Days_Left"], errors="coerce")

        st.markdown("### 📊 Breakdown by Source")
        st.write(df["Source"].value_counts())

        st.markdown(f"### 📑 Showing {len(df)} opportunities")

        display_df = df.drop(columns=["Clickable_Link"], errors="ignore")

        st.dataframe(display_df, use_container_width=True, height=600)

        with open("all_grants.xlsx", "rb") as f:
            st.download_button(
                label="⬇️ Download as Excel",
                data=f,
                file_name="all_grants.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("ℹ️ No data yet. Click Run Scraper to generate.")

# ------------------------------------------------------
# FOOTER
# ------------------------------------------------------
st.markdown(f"""
<footer>
    <div class="footer-grid">
        <div class="footer-col">
            <img src="data:image/png;base64,{logo_base64}" style="height:50px;">
            <p>The Metropolitan Institute is a think-and-do tank dedicated to building aspirational and resilient regions.</p>
        </div>
        <div class="footer-col">
            <h4>Quick Links</h4>
            <p><a href="about.html">About Us</a></p>
            <p><a href="research.html">Our Research</a></p>
            <p><a href="contact.html">Contact</a></p>
        </div>
        <div class="footer-col">
            <h4>Connect</h4>
            <p><a href="https://x.com/TheMetroInst">Twitter / X</a></p>
            <p><a href="https://www.linkedin.com/company/the-metropolitan-institute">LinkedIn</a></p>
            <p><a href="https://www.instagram.com/themetropolitaninstitute">Instagram</a></p>
        </div>
        <div class="footer-col">
            <h4>Support Our Mission</h4>
            <p>Help us bridge the gap between policy and people.</p>
        </div>
    </div>
    <div class="footer-bottom">
        © 2025 The Metropolitan Institute. All Rights Reserved.
    </div>
</footer>
""", unsafe_allow_html=True)
