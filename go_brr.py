#!/usr/bin/env python3

import argparse
import csv
import csv2pdf
import glob
import math
import os
import random
import rosters
import sys

OUT_PATH = "out"
HTML_PATH = os.path.expanduser("~/html/seating")

GREEN = "\033[0;32m"
END = "\033[0m"

def run(rooms, students):
    student_count = len(students)

    random.shuffle(students)
    seat_count = 0
    for img in glob.glob("images/*"):
        if img.split('.')[1] == "jpeg":
            os.rename(img, img.split('.')[0]+'.jpg')

    print(f"Preparing HTML directory '{HTML_PATH}'...")
    os.system(f"rm -r {HTML_PATH}")
    os.system(f"mkdir -p {HTML_PATH}")
    os.system(f"touch {HTML_PATH}/seat.csv")
    os.system(f"chmod 744 {HTML_PATH}/seat.csv")
    os.system(f"echo Uni, Name, Room, Seat >>  {HTML_PATH}/seat.csv")
    os.system(f"chmod 755 {HTML_PATH}")

    for _, count in rooms:
        seat_count += int(count)
    print("Total seats:", seat_count)

    for room in rooms:
        rname = room[0]
        path = os.path.join(OUT_PATH, rname)
        os.system(f"rm -rf {path}")
        os.mkdir(path)

        with open(os.path.join(path, "roster_" + rname + ".csv"), "w") as csvfile:
            output = csv.writer(csvfile)
            for i in range(math.ceil(student_count / seat_count * int(room[1]))):
                if len(students) > 0:
                    student = random.choice(students)
                    output.writerow(student)
                    students.remove(student)

        os.system("./seatingchart.py %s %s" %
                (rname, rname))
        os.system("cp %s/%s/chart_%s.html %s/%s.html" %
                (OUT_PATH, rname, rname, HTML_PATH, rname))

        # TODO Figure out what the hell this is doing
        os.system(f"perl -F, -lane 's/$F[2]/$F[2], {rname}/; print' {OUT_PATH}/{rname}/list_{rname}.csv >> {HTML_PATH}/seat.csv")
    
        os.system(f"chmod 644 {HTML_PATH}/{rname}.html")
    
    print("Copying images to HTML directory...")
    os.system(f"cp -r images {HTML_PATH}/images")
    os.system(f"chmod 711 {HTML_PATH}/images")
    os.system(f"chmod 644 {HTML_PATH}/images/*.*")

    csv2pdf.convert(f"{HTML_PATH}/seat.csv", f"{HTML_PATH}/seat.pdf")
    os.system(f"chmod 644 {HTML_PATH}/seat.pdf")
    os.system(f"rm {HTML_PATH}/seat.csv")

    print(GREEN+"Success!"+END)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Go brrr with the seating charts")

    parser.add_argument("rooms",
                        type=str,
                        metavar='<rooms_file>')

    parser.add_argument("roster",
                        type=str,
                        metavar='<roster_file>')


    args = parser.parse_args()

    students = rosters.load_roster(args.roster)
    print(f"Loaded {len(students)} students from {args.roster}")

    rooms = open(args.rooms, "r", newline='').readlines()
    rooms = map(str.strip, rooms) # remove leading/trailing whitespace
    rooms = filter(None, rooms) # remove empty strings
    rooms = map(lambda r: r.split(' '), rooms) # split on space to separate room from seat count
    rooms = list(rooms)

    print(f"Loaded {len(rooms)} rooms from {args.rooms}")

    run(rooms, students)

