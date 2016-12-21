#!/usr/bin/env python2

import csv, sys, os
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

"""
expects a csv file with assignments of the form:
uni,name,seat

name is ignored. Email is sent to uni@columbia.edu.
"""

#ADDRESS used as the reply-to address
ADDRESS = "cucs3157-tas@googlegroups.com"

#the message template, takes one variable which is replaced with the seat number
subj = "AP exam"
msg = "You are assigned seat %s."

if len(sys.argv) < 2:
    print "USAGE: %s <assignment_csv_filename>" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]

students = csv.reader(open(filename))

fromaddr = "foo@columbia.edu"
fromname = "Your Name"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(fromaddr, os.environ["LIONMAIL_DEVICE_PASS"])

for uni, toname, seat in students:
    print uni, msg % seat

    toaddr = "%s@columbia.edu" % uni

    email = MIMEMultipart()
    email["From"] = "%s <%s>" % (fromname, fromaddr)
    email["To"] = "%s <%s>" % (toname, toaddr)
    email["Subject"] = subj
    email["Reply-To"] = ADDRESS

    body = msg % seat
    email.attach(MIMEText(body, "plain"))

    text = email.as_string()
    server.sendmail(fromaddr, toaddr, text)

    time.sleep(0.1)

server.quit()
