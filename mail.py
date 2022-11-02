#!/usr/bin/env python3

import csv
import os
import smtplib
import time
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

"""
expects a csv file with assignments of the form:
name,seat,email
"""
# Parse arguments
parser = argparse.ArgumentParser(
    description="Cs3157 - Email students the seating arrangement")
parser.add_argument("email", type=str,
                    metavar="<sender_email>", help="Sender email address")
parser.add_argument("name", type=str,
                    metavar="<sender_name>", help="Sender name")
parser.add_argument("subject", type=str,
                    metavar="<subject>", help="Sender name")
parser.add_argument("list", type=str,
                    metavar="<student list>", help="Student list")
parser.add_argument("--re", type=str,
                    metavar="", default="cucs3157-tas@googlegroups.com", help="Reply to email")
args = parser.parse_args()

with open(args.list) as list:
    students = csv.reader(list)


def setup_server():
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(args.email, os.environ["LIONMAIL_DEVICE_PASS"])
    return server


server = None

DEFAULT_BACKOFF = 20  # seconds
next_backoff = DEFAULT_BACKOFF

for toname, seat, email_add in students:
    msg = f"Hi {toname}, your assigned seat is {seat}."
    print(f"{msg}, {email_add}.")

    toaddr = email_add
    email = MIMEMultipart()
    email["From"] = f"\"{args.name}\" <{args.email}>"
    email["To"] = f"\"{toname}\" <{toaddr}>"
    email["Subject"] = args.subject
    email["Reply-To"] = args.re

    email.attach(MIMEText(msg, "plain"))

    text = email.as_string()

    while True:
        try:
            if server == None:
                server = setup_server()
            server.sendmail(args.email, toaddr, text)
            time.sleep(1)
            next_backoff = DEFAULT_BACKOFF
            break
        except (smtplib.SMTPException, smtplib.SMTPServerDisconnected) as e:
            print(f"{e.smtp_code}: {e.smtp_error.decode()}")
            print(f"Waiting {next_backoff} seconds")
            time.sleep(next_backoff)
            next_backoff *= 2
            server = None

server.quit()
