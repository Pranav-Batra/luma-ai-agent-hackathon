import smtplib
import os
from dotenv import load_dotenv

load_dotenv() 
GMAIL_USER = os.environ.get("GMAIL_USER")  # your_email@gmail.com
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # app password
supa = os.environ.get("SUPABASE_URL")

print(supa)

print(GMAIL_USER)
print(GMAIL_APP_PASSWORD)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login("pranav.batra2006@gmail.com", "iczx nszv ridi gcxc")