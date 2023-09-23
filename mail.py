#!/usr/bin/env python3

import argparse
import csv
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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

parser.add_argument("reply_to",
                    type=str,
                    help="used as the reply-to address",
                    metavar='<reply-to>')

parser.add_argument("subject",
                    type=str,
                    help="the message template subject name",
                    metavar="<subject>")

parser.add_argument("from_name",
                    type=str,
                    help="the name of the sender",
                    metavar="<from-name>")

parser.add_argument("from_addr",
                    type=str,
                    help="the email address of the sender",
                    metavar="<from-addr>")

args = parser.parse_args()

#the message template, takes one variable which is replaced with the seat number
msg = "You are assigned seat %s."

filename = args.filename

file = open(filename)

students = csv.reader(file)

def setup_server():
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(args.from_addr, os.environ["LIONMAIL_DEVICE_PASS"])
    return server

server = None

DEFAULT_BACKOFF = 30 # seconds
next_backoff = DEFAULT_BACKOFF

for uni, to_name, seat in students:
    print(uni, msg % seat)

    to_addr = f"{uni}@columbia.edu"

    email = MIMEMultipart()
    email["From"] = f"\"{args.from_name}\" <{args.from_addr}>"
    email["To"] = f"\"{to_name}\" <{to_addr}>"
    email["Subject"] = args.subject
    email["Reply-To"] = args.reply_to

    body = msg % seat
    email.attach(MIMEText(body, "plain"))

    text = email.as_string()

    while True:
        try:
            if server == None:
                server = setup_server()
            server.sendmail(args.from_addr, to_addr, text)
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
