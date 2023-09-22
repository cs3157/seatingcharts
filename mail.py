#!/usr/bin/env python3

import csv
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse

"""
expects a csv file with assignments of the form:
uni,name,seat

name is ignored. Email is sent to uni@columbia.edu.
"""

# Creates a CLI argument parser
parser = argparse.ArgumentParser()

parser.add_argument("filename",
                    type=str,
                    help="filename of the seating chart",
                    metavar='<filename>')

parser.add_argument("address",
                    type=str,
                    help="used as the reply-to address",
                    metavar='<address>')

parser.add_argument("subj",
                    type=str,
                    help="the message template subject name",
                    metavar="<subj>")

parser.add_argument("fromname",
                    type=str,
                    help="the name of the sender",
                    metavar="<fromname>")

parser.add_argument("fromaddr",
                    type=str,
                    help="the email address of the sender",
                    metavar="<fromaddr>")

args = parser.parse_args()

#the message template, takes one variable which is replaced with the seat number
msg = "You are assigned seat %s."

filename = args.filename

file = open(filename)

students = csv.reader(file)

fromaddr = "kxc2103@columbia.edu"
fromname = "Kevin Chen"

def setup_server():
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(fromaddr, os.environ["LIONMAIL_DEVICE_PASS"])
    return server

server = None

DEFAULT_BACKOFF = 30 # seconds
next_backoff = DEFAULT_BACKOFF

for uni, toname, seat in students:
    print(uni, msg % seat)

    toaddr = f"{uni}@columbia.edu"

    email = MIMEMultipart()
    email["From"] = f"\{args.fromname}\{args.fromaddr}"
    email["To"] = f"\{toname}\{toaddr}"
    email["Subject"] = args.subj
    email["Reply-To"] = args.address

    body = msg % seat
    email.attach(MIMEText(body, "plain"))

    text = email.as_string()

    while True:
        try:
            if server == None:
                server = setup_server()
            server.sendmail(fromaddr, toaddr, text)
            time.sleep(1)
            next_backoff = DEFAULT_BACKOFF
            break
        except (smtplib.SMTPException, smtplib.SMTPServerDisconnected) as e:
            print(f"{e.smtp_code}: {e.smtp_error.decode()}")
            print(f"Waiting {next_backoff} seconds")
            time.sleep(next_backoff)
            next_backoff *= 2
            server = None

file.close()

server.quit()
