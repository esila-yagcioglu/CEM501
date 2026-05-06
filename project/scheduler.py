import schedule
import time
import subprocess
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def run_agent():
    print(f"\n[SCHEDULER] Running agent at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", "agent.py", "--dry-run"], cwd=os.path.dirname(__file__))


def run_digest():
    print(f"\n[SCHEDULER] Running digest at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", "digest.py"], cwd=os.path.dirname(__file__))


# Schedule jobs
schedule.every().day.at("08:00").do(run_agent)
schedule.every().day.at("08:00").do(run_digest)
schedule.every(30).minutes.do(run_agent)  # Also check every 30 min


if __name__ == "__main__":
    print("=" * 60)
    print("  CEM501 SCHEDULER STARTED")
    print("  Daily digest: every day at 08:00")
    print("  Email check: every 30 minutes")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    # Run once immediately on start
    print("\n[SCHEDULER] Running initial check...")
    run_digest()

    while True:
        schedule.run_pending()
        time.sleep(60)