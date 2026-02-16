from flask import Flask, render_template_string, send_file
import requests
import pandas as pd
import io
import time

app = Flask(__name__)

# 🔵 GitHub RAW Excel URL
EXCEL_URL = "https://raw.githubusercontent.com/RajuSakshena/all-scraping/main/all_grants.xlsx"

# Cache variables
cached_df = None
last_fetch_time = 0

# Auto refresh time (seconds)
CACHE_DURATION = 600   # 600 sec = 10 minutes


def get_excel_data():
    global cached_df, last_fetch_time

    current_time = time.time()

    # Reload if cache expired or first time
    if cached_df is None or (current_time - last_fetch_time) > CACHE_DURATION:

        response = requests.get(EXCEL_URL)

        if response.status_code != 200:
            raise Exception("Could not fetch file from GitHub")

        cached_df = pd.read_excel(io.BytesIO(response.content))
        cached_df = cached_df.fillna("")

        last_fetch_time = current_time

    return cached_df


@app.route("/")
def home():
    return "Flask App Running"


@app.route("/download")
def download_excel():
    try:
        response = requests.get(EXCEL_URL)

        if response.status_code != 200:
            return "Could not fetch file from GitHub", 404

        return send_file(
            io.BytesIO(response.content),
            download_name="all_grants.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return f"Download Error: {str(e)}", 500


@app.route("/jobs")
def jobs_dashboard():
    try:
        df = get_excel_data()

        table_html = df.to_html(index=False)

        html = f"""
        <html>
        <head>
            <title>Jobs Dashboard</title>
            <style>
                body {{
                    font-family: Arial;
                    padding: 20px;
                    background-color: #f4f6f9;
                }}
                h2 {{
                    margin-bottom: 15px;
                }}
                .download-btn {{
                    background: #58a648;
                    color: white;
                    padding: 10px 18px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                }}
                .download-btn:hover {{
                    background: #0b3c5d;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 14px;
                    background: white;
                }}
                th {{
                    background: #0b3c5d;
                    color: white;
                    padding: 8px;
                    text-align: left;
                }}
                td {{
                    padding: 6px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h2>Latest Job Listings</h2>

            <a class="download-btn" href="/download">
                Download Full Excel File
            </a>

            {table_html}
        </body>
        </html>
        """

        return render_template_string(html)

    except Exception as e:
        return f"Dashboard Error: {str(e)}", 500


if __name__ == "__main__":
    app.run()
