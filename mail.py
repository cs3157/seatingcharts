import csv, sys
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

for uni, name, seat in students:
    msg = "3157 Midterm: You are assigned seat %s."
    print uni, msg % seat
    mutt = Popen(["mutt", "-s", msg % seat, "%s@columbia.edu" % uni], stdin=PIPE)
    mutt.communicate(msg % seat)
    time.sleep(1)


