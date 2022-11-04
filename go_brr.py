#!/usr/bin/env python3

import argparse
import csv
import glob
import os
import random
import math
import seatingchart
import shutil
import pandas


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
            f"Total seats:{seat_count} > students:{student_count}, More seats than students; are you sure?")
    # fix jpeg in images
    for img in glob.glob(f"{image_path}/*"):
        if img.split('.')[1] == "jpeg":
            os.rename(img, img.split('.')[0]+'.jpg')
    html_path = os.path.expanduser(html_path)
    shutil.rmtree(html_path, ignore_errors=True)
    os.makedirs(html_path, mode=0o755, exist_ok=True)
    for room in rooms:
        rname = room[0]
        path = os.path.join(out_path, rname)
        shutil.rmtree(path)
        os.mkdir(path)
        # os.system(("ln -s %s %s" %
        #            ("images", path + "/" + "images")))
        with open(os.path.join(path, "roster_" + rname + ".csv"), "w") as csvfile:
            output = csv.writer(csvfile)
            for i in range(math.ceil(student_count / seat_count * int(room[1]))):
                if(len(students) > 0):
                    student = random.choice(students)
                    output.writerow(student)
                    students.remove(student)
            csvfile.flush()
        seatingchart.arrange_seat(rname, rname)
        shutil.copyfile(os.path.join(out_path, rname, f"chart_{rname}.html"),
                        os.path.join(html_path, f"{rname}.html"))
        os.chmod(os.path.join(html_path, f"{rname}.html"), mode=0o644)
    image_path = os.path.join(os.getcwd(), image_path)
    shutil.copytree(image_path, os.path.join(html_path, "images"))
    os.chmod(os.path.join(html_path, "images"), mode=0o711)
    # os.chmod can't do that
    os.system(f"chmod 644 {html_path}/images/*.*")

    print("\033[01;92mSuccess!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Go brrr with the seating charts")

    parser.add_argument("rooms",
                        type=str,
                        metavar='<rooms>', help='Room seats allocation')
    parser.add_argument("roster",
                        type=str,
                        metavar='<roster>', help='Student roster from courseworks')
    parser.add_argument("--out", "--O",
                        type=str, default="out",
                        metavar='', help='Output Path')
    parser.add_argument("--html", "--H",
                        type=str, default="~/html/seating",
                        metavar='', help='HTML Path')
    args = parser.parse_args()
    rooms_order = args.rooms
    student_list = args.roster
    main(args.rooms, args.roster, args.out, args.html)
