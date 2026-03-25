from flask import Flask, render_template_string, send_file, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import io
import time

app = Flask(__name__)
CORS(app)

EXCEL_URL = "https://raw.githubusercontent.com/RajuSakshena/all-scraping/main/all_grants.xlsx"

# Cache
cached_df = None
last_fetch_time = 0
CACHE_DURATION = 600  # 10 min


# ======================================================
# 🔥 FAST FETCH WITH TIMEOUT + RETRY
# ======================================================
def fetch_excel():
    for i in range(3):  # retry 3 times
        try:
            response = requests.get(EXCEL_URL, timeout=10)

            if response.status_code == 200:
                return response.content

        except Exception:
            time.sleep(2)

    raise Exception("❌ Failed to fetch Excel after retries")


def get_excel_data():
    global cached_df, last_fetch_time

    current_time = time.time()

    # ✅ Use cache if valid
    if cached_df is not None and (current_time - last_fetch_time) < CACHE_DURATION:
        return cached_df

    print("🔄 Fetching fresh data...")

    content = fetch_excel()

    df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    df = df.fillna("")

    # ✅ LIMIT rows for faster UI
    cached_df = df.head(300)

    last_fetch_time = current_time

    return cached_df


# ======================================================
# ROUTES
# ======================================================
@app.route("/")
def home():
    return "Flask App Running 🚀"


@app.route("/jobs-json")
def jobs_json():
    try:
        df = get_excel_data()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/download")
def download_excel():
    try:
        content = fetch_excel()

        return send_file(
            io.BytesIO(content),
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

        # ✅ fast render (no heavy HTML)
        rows = df.to_dict(orient="records")

        html_rows = ""
        for r in rows:
            html_rows += f"""
            <tr>
                <td>{r.get('Title','')}</td>
                <td>{r.get('Deadline','')}</td>
                <td>{r.get('Matched_Vertical','')}</td>
                <td><a href="{r.get('Apply_Link','')}" target="_blank">Apply</a></td>
            </tr>
            """

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

                .btn {{
                    background: #58a648;
                    color: white;
                    padding: 8px 14px;
                    border-radius: 6px;
                    text-decoration: none;
                    margin-right: 10px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background: white;
                }}

                th {{
                    background: #0b3c5d;
                    color: white;
                    padding: 8px;
                }}

                td {{
                    padding: 6px;
                    border-bottom: 1px solid #ddd;
                }}
            </style>
        </head>

        <body>

            <h2>🚀 Latest Job Listings</h2>

            <a class="btn" href="/download">Download Excel</a>
            <a class="btn" href="/jobs-json" target="_blank">View JSON</a>

            <table>
                <tr>
                    <th>Title</th>
                    <th>Deadline</th>
                    <th>Vertical</th>
                    <th>Apply</th>
                </tr>
                {html_rows}
            </table>

        </body>
        </html>
        """

        return render_template_string(html)

    except Exception as e:
        return f"Dashboard Error: {str(e)}", 500


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)
