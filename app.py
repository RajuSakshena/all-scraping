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
