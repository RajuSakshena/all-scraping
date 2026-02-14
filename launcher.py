import subprocess
import threading
import webview
import time
import sys
import os

PORT = "8501"

def run_streamlit():
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port", PORT,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.getcwd()
    )

if __name__ == "__main__":
    # Start Streamlit in background thread
    t = threading.Thread(target=run_streamlit, daemon=True)
    t.start()

    # Wait for server to start
    time.sleep(3)

    # Create desktop window
    webview.create_window(
        title="Grants & RFP Scraper",
        url=f"http://127.0.0.1:{PORT}",
        width=1200,
        height=800,
        resizable=True
    )

    webview.start()
