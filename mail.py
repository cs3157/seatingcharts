import csv, sys, os
from subprocess import call, Popen, PIPE
import time

"""
expects a csv file with assignments of the form:
uni,name,seat

name is ignored. Email is sent to uni@columbia.edu.
"""

#ADDRESS used as the reply-to address
ADDRESS = "cucs3157-tas@googlegroups.com"

#the message template, takes one variable which is replaced with the seat number
msg = "3157 exam: You are assigned seat %s."

if len(sys.argv) < 2:
    print "USAGE: %s <assignment_csv_filename>" % sys.argv[1]
    sys.exit(1)

filename = sys.argv[1]

students = csv.reader(open(filename))

#set mutt parameter
os.environ["REPLYTO"] = ADDRESS

for uni, name, seat in students:
    print uni, msg % seat
    mutt = Popen(["mutt", "-s", msg % seat, "%s@columbia.edu" % uni], stdin=PIPE, env=dict(os.environ, REPLYTO=ADDRESS))
    mutt.communicate(msg % seat)
    time.sleep(1)


