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
    overflow-x: hidden !important;
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
    background: #fff !important;
    color: #000 !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: 1px solid #000 !important;
    cursor: pointer;
    transition: 0.3s;
}
div.stDownloadButton > button:first-child:hover {
    background: #fff !important;
    color: #000 !important;
    border: 1px solid #000 !important;
}

/* Custom styling for Run Scraper button */
div.stButton > button:first-child {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background: #fff !important;
    color: #000 !important;
    font-weight: bold;
    border-radius: 6px;
    text-decoration: none;
    border: 1px solid #000 !important;
    cursor: pointer;
    transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background: #fff !important;
    color: #000 !important;
    border: 1px solid #000 !important;
}

/* Force black text in dataframe cells */
div[data-testid="stDataFrame"] td {
    color: #000 !important;
}

/* Force white theme overrides */
.stSidebar {
    background-color: white !important;
    color: black !important;
}
.stSidebar * {
    color: black !important;
}
.stApp > main {
    background-color: white !important;
}
[data-testid="stDataFrame"] {
    background-color: white !important;
}
th {
    background-color: white !important;
    color: black !important;
}
.stSlider label {
    color: black !important;
}
.stMultiSelect label {
    color: black !important;
}
label {
    color: black !important;
}
[data-testid="stDataFrame"] {
    overflow-x: auto !important;
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
    overflow-x: hidden !important;
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
    word-wrap: break-word;
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

/* Media queries for responsiveness */
@media (max-width: 1024px) {
    .footer-grid {
        grid-template-columns: 1fr 1fr;
    }
    .footer-col {
        margin-bottom: 2rem;
    }
}

@media (max-width: 768px) {
    .footer-grid {
        grid-template-columns: 1fr;
    }
    .navbar {
        justify-content: center;
        padding: 1rem 2% 0.5rem 2%;
    }
    .hero {
        padding: 30px 10px;
    }
    .hero h1 {
        font-size: 2em;
    }
    .hero p {
        font-size: 1em;
    }
    div.stButton > button:first-child,
    div.stDownloadButton > button:first-child {
        width: 100%;
    }
    .content {
        padding: 2rem 5%;
    }
}

@media (max-width: 480px) {
    .footer-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    .footer-col {
        margin-bottom: 1.5rem;
    }
    .navbar {
        padding: 0.5rem 2%;
    }
    .hero {
        padding: 20px 5px;
    }
    .hero h1 {
        font-size: 1.5em;
    }
    .hero p {
        font-size: 0.9em;
    }
    .content {
        padding: 1rem 2%;
    }
}
</style>
""", unsafe_allow_html=True)
