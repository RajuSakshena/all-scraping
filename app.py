from flask import Flask, render_template, send_file, redirect, url_for
import pandas as pd
import os
from combined_scraper import run_combined_scraper

app = Flask(__name__)

FILE_NAME = "all_grants.xlsx"

@app.route("/")
def home():
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        table = df.to_html(classes="table table-striped", index=False)
    else:
        table = None
    return render_template("index.html", table=table)


@app.route("/run")
def run_scraper():
    try:
        run_combined_scraper()
    except Exception as e:
        return f"Error occurred: {e}"
    return redirect(url_for("home"))


@app.route("/download")
def download_file():
    if os.path.exists(FILE_NAME):
        return send_file(FILE_NAME, as_attachment=True)
    return "File not found"


if __name__ == "__main__":
    app.run(debug=True)
