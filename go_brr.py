#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import random
import sys
import math
import seatingchart


def main(rooms_order: str, student_list: str, out_path: str = "out", html_path: str = "~/html/seating", image_path: str = "images"):
    students = [tuple(s) for s in csv.reader(open(student_list))][3:-30]
    random.shuffle(students)
    student_count = len(students)
    seat_count = 0
    # check if the total seats is enough
    with open(rooms_order, 'r') as f:
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

    for img in glob.glob(f"{image_path}/*"):
        if img.split('.')[1] == "jpeg":
            os.rename(img, img.split('.')[0]+'.jpg')

    os.system(f"rm -r {html_path}")
    os.system(f"mkdir -p {html_path}")
    os.system(f"touch {html_path}/seat.csv")
    os.system(f"chmod 744 {html_path}/seat.csv")
    os.system(f"chmod 755 {html_path}")

    for room in rooms:
        rname = room[0]
        path = os.path.join(out_path, rname)
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
        for i in range(math.ceil(student_count / seat_count * int(room[1]))):
            # for i in range(int(room[1])):
            if(len(students) > 0):
                student = random.choice(students)
                output.writerow(student)
                students.remove(student)
        csvfile.flush()
        seatingchart.arrange_seat(rname, rname)
        # os.system("./seatingchart.py %s %s" %
        #           (rname, rname))
        os.system("cp %s/%s/chart_%s.html %s/%s.html" %
                  (out_path, rname, rname, html_path, rname))
        os.system(
            f"perl -F, -lane 's/$F[2]/$F[2], {rname}/; print' {out_path}/{rname}/list_{rname}.csv >> {html_path}/seat.csv")
    #    os.system("cp %s/%s/list_%s.csv %s/%s.csv" %
    #              (out_path, rname, rname, html_path, rname))
        os.system(f"chmod 644 {html_path}/{rname}.html")
    os.system(f"cp -r images {html_path}/images")
    os.system(f"chmod 711 {html_path}/images")
    os.system(f"chmod 644 {html_path}/images/*.*")

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
    parser.add_argument("--out", "--O",
                        type=str, default="out",
                        metavar='Output Path')
    parser.add_argument("--html", "--H",
                        type=str, default="~/html/seating",
                        metavar='HTML Path')
    args = parser.parse_args()
    rooms_order = args.rooms
    student_list = args.roster
    main(args.rooms, args.roster, args.out, args.html)
