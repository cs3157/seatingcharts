#!/usr/bin/env python3

"""
Seating Chart script. See https://github.com/cs3157/seatingcharts
"""

import argparse
import itertools
import csv
import os
import random
import template


def assert_file_exists(path):
    if not os.path.isfile(path):
        print(f"Missing required file: {path}")
        exit(1)


def working_dir_path(name, slug, extension):
    """
    generates paths in the format:
    out/3157-2017-9-final/roster_3157-2017-9-final.html
    """
    filename = f"{name}_{slug}.{extension}"
    return os.path.join("out", slug, filename)


def arrange_seat(slug: str, layout: str, title: str = None, lefty: bool = False, debug: bool = False) -> None:
    # 1) a list of seats, in order of preference, with optionally ignored blank lines and repeats allowed
    #    basically tab/newline separated, with no difference between them
    SEATS_IN_ORDER = os.path.join("layouts", layout + "_ordered.txt")
    assert_file_exists(SEATS_IN_ORDER)

    # 1.5) a list of lefty seats, in order of preference, with optioonally ignored blank lines and
    #      repeats allowed, basically tab/newline separted with no difference between them
    if lefty:
        LSEATS_IN_ORDER = os.path.join(
            "layouts", layout + "_lefty_ordered.txt")
        assert_file_exists(LSEATS_IN_ORDER)

    # 2) a CSV list of students, one per line.
    # ie what you get if you download a gradebook from courseworks
    STUDENT_LIST = working_dir_path("roster", slug, "csv")
    assert_file_exists(STUDENT_LIST)

    # 2.5) a CSV list of students, one per line.
    # ie what you get if you download a gradebook from courseworks
    if lefty:
        LSTUDENT_LIST = working_dir_path("lefty_roster", slug, "csv")
        assert_file_exists(LSTUDENT_LIST)

    # two lists, of students to assign first and last
    assign_first_path = working_dir_path("assign-first", slug, "txt")
    assign_last_path = working_dir_path("assign-last",  slug, "txt")

    ASSIGN_FIRST = assign_first_path if os.path.isfile(
        assign_first_path) else "/dev/null"
    ASSIGN_LAST = assign_last_path if os.path.isfile(
        assign_last_path) else "/dev/null"

    # photos_path = os.path.join("out", slug, slug + "_files")
    photos_path = os.path.join(
        "images")

    # 3) a tsv file containing the format of the room
    layout_path = os.path.join("layouts", layout + ".txt")
    assert_file_exists(layout_path)
    LAYOUT = layout_path

    # outputs:
    TITLE = title if title != None else f"{slug} Seating"

    # a CSV student id ordered list of assigned seats
    OUTPUT_CSV = working_dir_path("list", slug, "csv")

    # a pretty HTML version of uni <-> seats
    OUTPUT_HTML = working_dir_path("list", slug, "html")

    # an html page with seat, student, and photo
    OUTPUT_CHART = working_dir_path("chart", slug, "html")

    # Now we're ready to assign seats
    assignments = {}

    with open(SEATS_IN_ORDER, "r") as f:
        seats = f.readlines()
    seats = [s for s in seats if s[0] != '#']  # Strip comments
    seats = list(itertools.chain.from_iterable(
        [z.strip().split() for z in seats]))

    assign_last = [x.strip() for x in open(ASSIGN_LAST).readlines()]
    assign_first = [x.strip() for x in open(ASSIGN_FIRST).readlines()]

    students = [tuple(s) for s in csv.reader(
        open(STUDENT_LIST))][2:]  # Skip two header rows
    random.shuffle(students)

    # the assign_first/last students are shuffled randomly, so we need to pull them to the front/back
    reassign = [x for x in students if x[0] in assign_last]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)
    students.reverse()

    reassign = [x for x in students if x[0] in assign_first]
    for x in reassign:
        students.remove(x)
    students.extend(reassign)

    # now loop over ordered seats assigning students
    for seat in seats:
        if seat and seat not in assignments:
            try:
                assignments[seat] = students.pop()
            except:
                # Assigned all students
                break
            if debug:
                print("assigned", assignments[seat], "to", seat)
    if students:
        print("WARNING: unassigned students", students)

    if lefty:
        with open(LSEATS_IN_ORDER, "r") as f:
            lseats = f.readlines()
        lseats = [s for s in lseats if s[0] != "#"]
        lseats = list(itertools.chain.from_iterable(
            [z.strip().split() for z in lseats]))

        lstudents = [tuple(s) for s in csv.reader(open(LSTUDENT_LIST))][2:]
        random.shuffle(lstudents)

        for lseat in lseats:
            if lseat and lseat not in assignments:
                try:
                    assignments[lseat] = lstudents.pop()
                except:
                    # All lefties assigned
                    break
                if debug:
                    print("assigned lefty", assignments[lseat], "to", lseat)
        if lstudents:
            print("WARNING: unassigned lefties", lstudents)

    # Write out the HTML roster
    with open(OUTPUT_HTML, "w") as html:
        html.write(template.css.format(TITLE))
        # sort by uni
        for seat, student in sorted(assignments.items(), key=lambda x: x[1][0]):
            # for seat, student in assignments.items():
            html.write(
                f"""<div><span class="uni">{student[0]}</span> <span class="seat">{seat}</span></div>""")
        html.write("""</div></body>\n""")

    # dump to CSV as well
    output = csv.writer(open(OUTPUT_CSV, "w"))
    for seat, uni in assignments.items():
        output.writerow(list(uni)[:2] + [seat])

    # Write the chart
    room = [s for s in csv.reader(open(LAYOUT), delimiter="\t")]
    maxrow = max([len(x) for x in room])

    with open(OUTPUT_CHART, "w") as seating_chart:
        seating_chart.write(template.header)
        for row in room:
            seating_chart.write("<tr>")
            row_count = 0

            for seat in row:
                row_count = row_count + 1
                seating_chart.write(
                    "<td class='unselected' onclick='selectStudent(this)' >\n")

                try:
                    student = assignments[seat]
                    uni = student[0]
                    name = student[1]
                    full_name = student[1].split(", ")
                    full_name = f"{full_name[1]} {full_name[0]}"
                    # Used to check if file exists
                    # img_path = os.path.join(photos_path, uni + ".jpg")
                    img_path = os.path.join(photos_path, name + ".jpg")
                    # img_rel_path = os.path.join(
                    #     slug + "_files", uni + ".jpg")  # Inserted into HTML
                    img_rel_path = os.path.join(
                        photos_path, name + ".jpg")  # Inserted into HTML
                    if os.path.isfile(img_path):
                        seating_chart.write(
                            f"""<span class="seat">{seat}</span><br> {uni}<br> <span class="name">{name}</span><br> <img src="{img_rel_path}">""")
                    else:
                        print(f"WARNING: no img found for {img_path}")
                        seating_chart.write(
                            f"""<span class="seat">{seat}</span><br> {uni}<br> <span class="name">{name}</span><br> """)
                except KeyError:
                    seating_chart.write(
                        f"""<span class="seat">{seat}</span>""")
                seating_chart.write("</td>\n")

            for i in range(maxrow - row_count):
                seating_chart.write("<td></td>\n")

            seating_chart.write("</tr>\n\n")
        seating_chart.write("</table></body>")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate a seating chart based on the course roster")

    parser.add_argument("slug",
                        type=str,
                        help="the \"out\" subdirectory to use as the working directory",
                        metavar='<slug>')

    parser.add_argument("layout",
                        type=str,
                        help="the seating chart layout (classroom name) to use",
                        metavar="<layout>")

    parser.add_argument("-t", "--title",
                        default=None, type=str,
                        help="human-readable name that will be written the top of seating chart",
                        metavar="<title>")

    parser.add_argument("-l", "--lefty",
                        action="store_true",
                        help="assign seats to lefty students")

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="print debug messages")

    args = parser.parse_args()
    arrange_seat(args.slug, args.layout, args.title, args.lefty, args.debug)
