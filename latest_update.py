import subprocess
import csv
import time
from datetime import datetime
import os

# Path to your adb.exe
ADB_PATH = r"C:\Users\libon\OneDrive\문서\platform-tools\adb.exe"

# Configurable wait time before taking screenshot
WAIT_BEFORE_SCREENSHOT = 10  # seconds

def run_adb_command(args):
    """Run adb command and return output"""
    try:
        result = subprocess.run([ADB_PATH] + args, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ADB command failed: {' '.join(args)}\n{e}")
        return None

def open_sms_app_and_screenshot(phone_number, message, reg_num):
    """Open SMS app, wait, take screenshot, and save locally with reg_num as filename"""
    safe_message = message.replace("'", r"'\''")
    shell_cmd = f"am start -a android.intent.action.SENDTO -d sms:{phone_number} --es sms_body '{safe_message}'"
    print(f"\nOpening SMS app for {phone_number}...")
    run_adb_command(["shell", shell_cmd])

    print(f"Waiting {WAIT_BEFORE_SCREENSHOT} seconds to allow manual sending on device...")
    time.sleep(WAIT_BEFORE_SCREENSHOT)

    local_folder = "screenshots"
    os.makedirs(local_folder, exist_ok=True)

    device_screenshot_path = f"/sdcard/{reg_num}.png"
    local_screenshot_path = os.path.join(local_folder, f"{reg_num}.png")

    print(f"Taking screenshot for {reg_num}...")
    run_adb_command(["shell", "screencap", "-p", device_screenshot_path])

    print(f"Pulling screenshot to PC...")
    run_adb_command(["pull", device_screenshot_path, local_screenshot_path])

    print(f"Deleting screenshot from device...")
    run_adb_command(["shell", "rm", device_screenshot_path])

    print(f"Screenshot saved: {local_screenshot_path}")

# ================= MAIN SCRIPT =================
with open("students.csv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        phone = row.get("Parent Contact", "").strip()
        name = row.get("Name", "").strip()
        reg_num = row.get("Register Number", "").strip()
        total_classes = row.get("Total Classes", "").strip()
        attended = row.get("Attended", "").strip()
        attendance = row.get("Attendance Percentage", "").strip()

        if not phone or not name or not reg_num or not total_classes or not attended or not attendance:
            print(f"Skipping incomplete data: {row}")
            continue

        # SMS message (Telugu + English)
        message = (
            f"SVCET – హాజరు సమాచారం\n"
            f"విద్యార్థి: {name} ({reg_num})\n"
            f"విభాగం: కంప్యూటర్ సైన్స్ & ఇంజనీరింగ్ (AI)\n"
            f"హాజరు వివరాలు\n"
            f"•\tమొత్తం తరగతులు: {total_classes}\n"
            f"•\tహాజరైనవి: {attended}\n"
            f"•\tశాతం: {attendance}%\n"
            f"కనీసం 75% హాజరు తప్పనిసరి.\n"
            f"దయచేసి నియమిత హాజరు ఉండేలా చూడండి.\n"
            f"విభాగాధిపతి, CSE(AI)\n"
            f"9985187289 / 9949223384 \n\n"
            f"SVCET – Attendance Information\n"
            f"Student: {name} ({reg_num})\n"
            f"Department: CSE(AI)\n"
            f"Attendance Details\n"
            f"•\tTotal Classes: {total_classes}\n"
            f"•\tAttended: {attended}\n"
            f"•\tPercentage: {attendance}%\n"
            f"Minimum 75% attendance is mandatory.\n"
            f"Kindly ensure regular attendance.\n"
            f"Head of the Department, CSE(AI)\n"
            f"9985187289 / 9949223384"
        )

        open_sms_app_and_screenshot(phone, message, reg_num)
