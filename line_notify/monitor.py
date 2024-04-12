# monitor.py
import schedule
import time
import subprocess

def run_main_script():
    subprocess.run(["python3", "main.py"])

# Schedule the job to run every Monday at 7:00 AM GMT+7
schedule.every().monday.at("07:00").do(run_main_script)

# Main loop to run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
