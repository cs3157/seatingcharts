#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import random
import sys
import math
import seatingchart


def main():
    students = [tuple(s) for s in csv.reader(open(STUDENT_LIST))]
    random.shuffle(students)
    student_count = len(students)
    seat_count = 0
    for img in glob.glob("images/*"):
        if img.split('.')[1] == "jpeg":
            os.rename(img, img.split('.')[0]+'.jpg')

    os.system(f"rm -r {HTML_PATH}")
    os.system(f"mkdir -p {HTML_PATH}")
    os.system(f"touch {HTML_PATH}/seat.csv")
    os.system(f"chmod 744 {HTML_PATH}/seat.csv")
    os.system(f"chmod 755 {HTML_PATH}")

    with open(ROOMS_IN_ORDER, 'r') as f:
        rooms = f.readlines()
    rooms = [r for r in rooms if r != '\n']
    rooms = list([z.strip().split() for z in rooms])
    print(f"rooms:{rooms}")
    for _, count in rooms:
        seat_count += int(count)
    if seat_count == student_count:
        print(f"Total seats:{seat_count}")
    elif seat_count < student_count:
        print(
            f"Total seats:{seat_count} < students:{student_count}, it won't work!")
        return
    elif seat_count > student_count:
        print(
            f"Total seats:{seat_count} > students:{student_count}, are you sure?")

    for room in rooms:
        rname = room[0]
        path = os.path.join(OUT_PATH, rname)
        os.system("rm -rf %s" % path)
        os.mkdir(path)
        os.system(("ln -s %s %s" %
                   ("images", path + "/" + "images")))
        # print(("cp %s %s" %
        #        ("images", path + "/" + "images")))
        # os.system(("cp -rf %s %s" %
        #            ("images", path + "/" + "images")))
        csvfile = open(os.path.join(path, "roster_" + rname + ".csv"), "w")
        output = csv.writer(csvfile)
        # output.writerow("")
        # output.writerow("")
        # for i in range(math.ceil(student_count / seat_count * int(room[1]))):
        for i in range(int(room[1])):
            #    for i in range(int(room[1])):
            if(len(students) > 0):
                student = random.choice(students)
                output.writerow(student)
                students.remove(student)
        csvfile.flush()
        seatingchart.arrange_seat(rname, rname)
        # os.system("./seatingchart.py %s %s" %
        #           (rname, rname))
        os.system("cp %s/%s/chart_%s.html %s/%s.html" %
                  (OUT_PATH, rname, rname, HTML_PATH, rname))
        os.system(
            f"perl -F, -lane 's/$F[2]/$F[2], {rname}/; print' {OUT_PATH}/{rname}/list_{rname}.csv >> {HTML_PATH}/seat.csv")
    #    os.system("cp %s/%s/list_%s.csv %s/%s.csv" %
    #              (OUT_PATH, rname, rname, HTML_PATH, rname))
        os.system("chmod 644 %s/%s.html" % (HTML_PATH, rname))
    os.system("cp -r images %s/images" % HTML_PATH)
    os.system("chmod 711 %s/images" % HTML_PATH)
    os.system("chmod 644 %s/images/*.*" % HTML_PATH)

    print("\033[01;92mSuccess!")


if __name__ == "__main__":
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
    OUT_PATH = "out"
    HTML_PATH = "~/html/seating"
    main()
