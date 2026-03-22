import smtplib
from email.message import EmailMessage

import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD") # myaccount.google.com/apppasswords
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def send_alert(cid, contents):

    email = EmailMessage()
    email["Subject"] = f"Safety Alert - Clinician #{cid}"
    email.set_content(contents)
    email["From"] = SENDER_EMAIL
    email["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            s.send_message(email)
    except Exception as e:
        error_msg = f"[EMAIL] Failed to send alert for clinician #{cid}, contents: {contents} : {e}"
        with open("errors.txt", "a") as f:
            f.write(error_msg)
