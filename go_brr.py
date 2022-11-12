#!/usr/bin/env python3


from argparse import ArgumentParser
import csv
import glob
import math
import os
from random import shuffle, choice
from shutil import copytree, rmtree, copyfile

from seatingchart import arrange_seat


def main(rooms_order: str, student_list: str, out_path: str = "out",
         html_path: str = "~/html/seating", image_path: str = "images", lefty: bool = False):

    with open(student_list) as s_l:
        students = [tuple(s) for s in csv.reader(s_l)][3:]
    shuffle(students)
    student_count = len(students)
    seat_count = 0
    l_student_list = os.path.join("lefty_" + student_list)
    with open(l_student_list) as l_l:
        l_students = [tuple(s) for s in csv.reader(l_l)]
    shuffle(l_students)
    student_count = len(students)
    # check if the total seats is enough
    with open(rooms_order, 'r') as f:
        rooms = f.readlines()
    rooms = [r for r in rooms if r != '\n']
    rooms = [z.strip().split() for z in rooms]
    print(f"rooms:{rooms}")

    for _, count, lefty in rooms:
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
        if img.split('.')[-1] == "jpeg":
            os.rename(img, img.split('.')[:-1]+'.jpg')
    html_path = os.path.expanduser(html_path)
    try:
        rmtree(os.path.join(out_path), ignore_errors=True)
        os.makedirs(os.path.join(out_path), mode=0o755, exist_ok=True)
    except OSError:
        pass
    rmtree(html_path, ignore_errors=True)
    os.makedirs(html_path, mode=0o755, exist_ok=True)

    for rname, num, lefty in rooms:
        path = os.path.join(out_path, rname)
        os.mkdir(path)
        with open(os.path.join(path, "roster_" + rname + ".csv"), "w") as csvfile:
            output = csv.writer(csvfile)

            for _ in range(int(num)):
                # for i in range(math.ceil(student_count / seat_count * int(num))):
                if (len(students) > 0):
                    student = choice(students)
                    output.writerow(student)
                    students.remove(student)

            csvfile.flush()

        if int(lefty):
            with open(os.path.join(path, "lefty_roster_" + rname + ".csv"), "w") as csvfile:
                output = csv.writer(csvfile)

                for _ in range(int(lefty)):
                    # for i in range(math.ceil(student_count / seat_count * int(num))):
                    if (len(l_students) > 0):
                        l_student = choice(l_students)
                        output.writerow(l_student)
                        l_students.remove(l_student)

                csvfile.flush()
            arrange_seat(rname, rname, lefty=True)
        else:
            arrange_seat(rname, rname, lefty=False)
        # lefty seat
        copyfile(os.path.join(out_path, rname, f"chart_{rname}.html"), os.path.join(
            html_path, f"{rname}.html"))
        os.chmod(os.path.join(html_path, f"{rname}.html"), mode=0o644)
    image_path = os.path.join(os.getcwd(), image_path)
    copytree(image_path, os.path.join(html_path, "images"))
    os.chmod(os.path.join(html_path, "images"), mode=0o711)
    # os.chmod can't do that
    os.system(f"chmod 644 {html_path}/images/*.*")

    print("\033[01;92mSuccess!")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Go brrr with the seating charts")
    parser.add_argument("rooms",
                        type=str,
                        metavar='<rooms>', help='Room seats allocation')
    parser.add_argument("roster",
                        type=str,
                        metavar='<roster>', help='Student roster from courseworks')
    parser.add_argument("--out", "-o",
                        type=str, default="out",
                        metavar='', help='Output Path')
    parser.add_argument("--html",
                        type=str, default="~/html/seating",
                        metavar='', help='HTML Path')
    parser.add_argument("--lefty", "-l",
                        type=bool, default=False,
                        metavar='', help='Lefty Students')
    args = parser.parse_args()

    main(args.rooms, args.roster, args.out, args.html)
