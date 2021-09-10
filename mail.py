#!/usr/bin/env python3

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

#ADDRESS used as the reply-to address
ADDRESS = "cucs4118-tas@googlegroups.com"

#the message template, takes one variable which is replaced with the seat number
subj = "OS Exam 1"
msg = "You are assigned seat %s."

if len(sys.argv) < 2:
    print("USAGE: %s <assignment_csv_filename>" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]

students = csv.reader(open(filename))

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

    toaddr = "%s@columbia.edu" % uni

    email = MIMEMultipart()
    email["From"] = "\"%s\" <%s>" % (fromname, fromaddr)
    email["To"] = "\"%s\" <%s>" % (toname, toaddr)
    email["Subject"] = subj
    email["Reply-To"] = ADDRESS

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
            print(e)
            print("Waiting %s seconds" % next_backoff)
            time.sleep(next_backoff)
            next_backoff *= 2
            server = None

server.quit()
