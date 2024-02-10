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

parser.add_argument("-a", "--from_addr",
                    type=str,
                    default="do.not.reply@cloud.cs.columbia.edu",
                    help="the email address of the sender",
                    metavar="<from-addr>")

parser.add_argument("-s", "--subject",
        type=str,
        default='',
        help='subject line for the emails sent, default is no subject')

parser.add_argument("-n", "--sender",
        type=str,
        default='3157 Teaching Staff',
        help='sender name for emails, default="3157 Teaching Staff"')

parser.add_argument("-r", "--reply_to",
        type=str,
        default='cucs3157-tas@googlegroups.com',
        help='reply-to email address, default="cucs3157-tas@googlegroups.com"')

args = parser.parse_args()

#the message template, takes one variable which is replaced with the seat number
msg = "You are assigned seat %s."

filename = args.filename

file = open(filename)

students = csv.reader(file)

def setup_server():
    server = smtplib.SMTP("smtp-relay.gmail.com", 587)
    server.starttls()
    return server

server = None

DEFAULT_BACKOFF = 30 # seconds
next_backoff = DEFAULT_BACKOFF

for uni, to_name, seat in students:
    print(uni, msg % seat)

    to_columbia = f"{uni}@columbia.edu"
    to_barnard = f"{uni}@barnard.edu"
    recipients = [to_columbia, to_barnard]

    email = MIMEMultipart()
    email["From"] = f"\"{args.sender}\" <args.from_addr>"
    email["To"] = ", ".join(recipients)
    email["Subject"] = args.subject
    email["Reply-To"] = args.reply_to

    body = msg % seat
    email.attach(MIMEText(body, "plain"))

    text = email.as_string()

    while True:
        try:
            if server == None:
                server = setup_server()
            server.sendmail(args.from_addr, recipients, text)
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
