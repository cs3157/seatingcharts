import csv, sys, os
from subprocess import call, Popen, PIPE
import time

"""
expects a csv file with assignments of the form:
uni,name,seat

name is ignored. Email is sent to uni@columbia.edu.
"""


if len(sys.argv) < 2:
    print "USAGE: %s <assignment_csv_filename>" % sys.argv[1]
    sys.exit(1)

filename = sys.argv[1]

students = csv.reader(open(filename))

#set mutt parameter
os.environ["REPLYTO"] = "cucs3157-tas@googlegroups.com"

for uni, name, seat in students:
    msg = "3157 exam: You are assigned seat %s."
    print uni, msg % seat
    mutt = Popen(["mutt", "-s", msg % seat, "%s@columbia.edu" % uni], stdin=PIPE, env=dict(os.environ, REPLYTO="cucs3157-tas@googlegroups.com"))
    mutt.communicate(msg % seat)
    time.sleep(1)


