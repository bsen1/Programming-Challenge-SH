import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "briansen124@gmail.com"
SENDER_APP_PASSWORD = "ehba cqqt ahdx miyr"
RECEIVER_EMAIL = "briansen142@gmail.com"

def send_alert(cid, contents):

    email = EmailMessage()
    email["Subject"] = f"Safety Alert - Clinician #{cid}"
    email.set_content(contents)
    email["From"] = SENDER_EMAIL
    email["To"] = RECEIVER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        s.send_message(email)
        