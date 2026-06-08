"""
CEM501 — Launcher
Starts both the web dashboard and Telegram bot together.
Run with: python run.py
"""

import subprocess
import sys
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_dashboard():
    subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "dashboard.py")],
        cwd=BASE_DIR
    )


def run_telegram():
    # Give dashboard a second to start first
    time.sleep(2)
    subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "telegram_channel.py")],
        cwd=BASE_DIR
    )


if __name__ == "__main__":
    print("=" * 60)
    print("  CEM501 COMMUNICATION AGENT")
    print("  Starting dashboard + Telegram bot...")
    print("  Dashboard : http://localhost:5050")
    print("  Ctrl+C to stop everything")
    print("=" * 60)

    t = threading.Thread(target=run_telegram, daemon=True)
    t.start()

    # Dashboard runs in main thread (blocking)
    run_dashboard()