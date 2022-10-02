#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import random
import sys
import math

OUT_PATH = "out"
HTML_PATH = "html/seating"

parser = argparse.ArgumentParser(
    description="Go brrr with the seating charts")

parser.add_argument("rooms",
                    type=str,
                    metavar='<rooms>')

parser.add_argument("roster",
                    type=str,
                    metavar='<roster>')


args = parser.parse_args()
ROOMS_IN_ORDER = args.rooms
STUDENT_LIST = args.roster

students = [tuple(s) for s in csv.reader(open(STUDENT_LIST))][3:]
random.shuffle(students)
student_count = len(students)
seat_count = 0
for img in glob.glob("images/*"):
    if img.split('.')[1] == "jpeg":
        os.rename(img, img.split('.')[0]+'.jpg')

with open(ROOMS_IN_ORDER, 'r') as f:
    rooms = f.readlines()
rooms = [r for r in rooms if r != '\n']
rooms = list([z.strip().split() for z in rooms])
print(f"rooms:{rooms}")
for _, count in rooms:
    seat_count += int(count)

for room in rooms:
    rname = room[0]
    path = os.path.join(OUT_PATH, rname)
    os.system("rm -rf %s" % path)
    os.mkdir(path)
    print(("cp %s %s" %
           ("images", path + "/" + "images")))
    os.system(("cp -rf %s %s" %
               ("images", path + "/" + "images")))
    csvfile = open(os.path.join(path, "roster_" + rname + ".csv"), "w")
    output = csv.writer(csvfile)
    output.writerow("")
    output.writerow("")
    for i in range(math.ceil(student_count / seat_count * int(room[1]))):
        if(len(students) > 0):
            student = random.choice(students)
            output.writerow(student)
            students.remove(student)
    csvfile.flush()
    os.system("./seatingchart.py %s %s" %
              (rname, rname))
    os.system("cp %s/%s/chart_%s.html %s/%s.html" %
              (OUT_PATH, rname, rname, HTML_PATH, rname))
    os.system("chmod a+xr %s/%s.html" % (HTML_PATH, rname))

print("\033[01;92mSuccess!")
