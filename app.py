from flask import Flask, render_template_string, send_file, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import io
import time

app = Flask(__name__)

# Enable CORS so frontend (localhost or website) can access API
CORS(app)

# 🔵 GitHub RAW Excel URL
EXCEL_URL = "https://raw.githubusercontent.com/RajuSakshena/all-scraping/main/all_grants.xlsx"

# Cache variables
cached_df = None
last_fetch_time = 0

# Cache duration (seconds)
CACHE_DURATION = 600  # 10 minutes


def get_excel_data():
    global cached_df, last_fetch_time

    current_time = time.time()

    # Reload if cache expired or first request
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
    return "Flask API Running"


# ===============================
# JSON API
# ===============================
@app.route("/jobs-json")
def jobs_json():
    try:
        df = get_excel_data()

        data = df.to_dict(orient="records")

        return jsonify(data)

    except Exception as e:
        return {"error": str(e)}, 500


# ===============================
# DOWNLOAD EXCEL
# ===============================
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


# ===============================
# DASHBOARD PAGE
# ===============================
@app.route("/jobs")
def jobs_dashboard():
    try:
        df = get_excel_data()

        table_html = df.to_html(index=False)

        html = f"""
        <html>
        <head>
            <title>NGO Grants Dashboard</title>

            <style>

            body {{
                font-family: Arial;
                padding: 20px;
                background-color: #f4f6f9;
            }}

            h2 {{
                margin-bottom: 15px;
            }}

            .button-group {{
                margin-bottom: 20px;
            }}

            .download-btn {{
                background: #58a648;
                color: white;
                padding: 10px 18px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                margin-right: 10px;
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

        <h2>Latest NGO Grants</h2>

        <div class="button-group">

            <a class="download-btn" href="/download">
                Download Excel
            </a>

            <a class="download-btn" href="/jobs-json" target="_blank">
                View JSON API
            </a>

        </div>

        {table_html}

        </body>
        </html>
        """

        return render_template_string(html)

    except Exception as e:
        return f"Dashboard Error: {str(e)}", 500


if __name__ == "__main__":
    app.run()
