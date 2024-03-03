#!/usr/bin/env python3

"""
Seating Chart script. See https://github.com/cs3157/seatingcharts
"""

import argparse
import csv
import itertools
import random
import rosters
from pathlib import Path

def assert_file_exists(path):
    if not path.is_file():
        print(f"Missing required file: {path}")
        exit(1)


def working_dir_path(name, slug, extension):
    """
    generates paths in the format:
    out/3157-2017-9-final/roster_3157-2017-9-final.html
    """
    filename = f"{name}_{slug}.{extension}"
    return Path("out") / slug / filename


def main(args):
    # 1) a list of seats, in order of preference, with optionally ignored blank lines and repeats allowed
    #    basically tab/newline separated, with no difference between them
    SEATS_IN_ORDER = Path("layouts") / f"{args.layout}_ordered.txt"
    assert_file_exists(SEATS_IN_ORDER)

    # 1.5) a list of lefty seats, in order of preference, with optionally ignored blank lines and
    #      repeats allowed, basically tab/newline separated with no difference between them
    if args.lefty:
        LSEATS_IN_ORDER = Path("layouts") / f"{args.layout}_lefty_ordered.txt"
        assert_file_exists(LSEATS_IN_ORDER)

    # 2) a CSV list of students, one per line.
    # i.e., what you get if you download a gradebook from courseworks
    STUDENT_LIST = working_dir_path("roster", args.slug, "csv")
    assert_file_exists(STUDENT_LIST)

    # 2.5) a CSV list of students, one per line.
    # i.e., what you get if you download a gradebook from courseworks
    if args.lefty:
        LSTUDENT_LIST = working_dir_path("lefty_roster", args.slug, "csv")
        assert_file_exists(LSTUDENT_LIST)

    # two lists, of students to assign first and last
    assign_first_path = working_dir_path("assign-first", args.slug, "txt")
    assign_last_path = working_dir_path("assign-last", args.slug, "txt")

    ASSIGN_FIRST = assign_first_path if assign_first_path.is_file() else "/dev/null"
    ASSIGN_LAST = assign_last_path if assign_last_path.is_file() else "/dev/null"

    photos_path = Path("images")

    # 3) a tsv file containing the format of the room
    layout_path = Path("layouts") / f"{args.layout}.txt"
    assert_file_exists(layout_path)
    LAYOUT = layout_path

    # outputs:
    TITLE = args.title if args.title is not None else f"{args.slug} Seating"

    # a CSV student id ordered list of assigned seats
    OUTPUT_CSV = working_dir_path("list", args.slug, "csv")

    # a pretty HTML version of uni <-> seats
    OUTPUT_HTML = working_dir_path("list", args.slug, "html")

    # an HTML page with seat, student, and photo
    OUTPUT_CHART = working_dir_path("chart", args.slug, "html")

    # Now we're ready to assign seats
    assignments = {}

    with open(SEATS_IN_ORDER, "r") as f:
        seats = f.readlines()

    seats = [s for s in seats if s[0] != '#']  # Strip comments
    seats = list(itertools.chain.from_iterable([z.strip().split() for z in seats]))  # Split on whitespace and flatten

    with open(ASSIGN_LAST, "r") as f:
        assign_last = [x.strip() for x in f.readlines()]

    with open(ASSIGN_FIRST, "r") as f:
        assign_first = [x.strip() for x in f.readlines()]

    students = rosters.load_roster(STUDENT_LIST)

    random.shuffle(students)

    # the assign_first/last students are shuffled randomly, so we need to pull them to the front/back
    reassign = [s for s in students if s[0] in assign_last] # s[0] is the UNI
    for s in reassign:
        students.remove(s)
    students.extend(reassign)
    students.reverse()

    reassign = [s for s in students if s[0] in assign_first]
    for s in reassign:
        students.remove(s)
    students.extend(reassign)

    # now loop over ordered seats assigning students
    for seat in seats:
        if seat and seat not in assignments:
            try:
                assignments[seat] = students.pop()
            except:
                # Assigned all students
                break
            if args.debug:
                print("assigned", assignments[seat], "to", seat)
    if students:
        print("WARNING: unassigned students", students)

    if args.lefty:
        with open(LSEATS_IN_ORDER, "r") as f:
            lseats = f.readlines()
        lseats = [s for s in lseats if s[0] != "#"]
        lseats = list(itertools.chain.from_iterable([z.strip().split() for z in lseats]))

        lstudents = rosters.load_roster(LSTUDENT_LIST)
        random.shuffle(lstudents)

        for lseat in lseats:
            if lseat and lseat not in assignments:
                try:
                    assignments[lseat] = lstudents.pop()
                except:
                    # All lefties assigned
                    break
                if args.debug:
                    print("assigned lefty", assignments[lseat], "to", lseat)
        if lstudents:
            print("WARNING: unassigned lefties", lstudents)

    # Write out the HTML roster
    with open(OUTPUT_HTML, "w") as html:
        html.write("""<style>
                .seat {
                    padding-left: 1em;
                    margin-bottom: .2em;
                }
                .name {
                    font-size: 9pt;
                }
                .assignments {
                    -webkit-column-count: 4; /* Chrome, Safari, Opera */
                    -moz-column-count: 4; /* Firefox */
                    column-count: 4;
                }
                h3 {
                    text-align: center;
                }
                </style>
        <body>
        <h3>%s</h3>
        <div class="assignments">\n\n""" % TITLE)
        for seat, student in sorted(assignments.items(), key=lambda x: x[1][0]):  # sort by uni
            html.write(f'<div><span class="uni">{student[0]}</span> <span class="seat">{seat}</span></div>')
        html.write('</div></body>\n')

    # dump to CSV as well
    with open(OUTPUT_CSV, "w") as output:
        csv_output = csv.writer(output)
        for seat, student in assignments.items():
            csv_output.writerow(list(student) + [seat])

    # Write the chart
    with open(LAYOUT) as layout:
        room = [s for s in csv.reader(layout, delimiter="\t")]
        maxrow = max([len(x) for x in room])

    with open(OUTPUT_CHART, "w") as seating_chart:
        seating_chart.write("""
        <style>
                table {
                    table-layout: fixed;
                    width: 100%;
                }
                img {
                    width: 60px;
                    vertical-align: text-bottom;
                }
                .seat {
                    font-weight: bold;
                    font-size: 14pt;
                    vertical-align: top;
                }
                .name {
                    font-size: 9pt;
                }
                td {
                    text-align: center;
                    vertical-align: baseline;
                    width: 70px;
                }
                .unselected {
                    background-color: white;
                }
                .selected {
                    background-color: orange;
                }
        </style>

        <script>
            function selectStudent(cell) {
                if (cell.className === "unselected") {
                    cell.className = "selected";
                } else {
                    cell.className = "unselected";
                }
            }
        </script>
        <body><table border=1>\n\n""")

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
                    full_name = name.split(", ")
                    full_name = f"{full_name[1]} {full_name[0]}"

                    # Used to check if file exists
                    img_path = photos_path / f"{uni}.jpg"
                    img_rel_path = photos_path / f"{uni}.jpg"  # Inserted into HTML
                    if img_path.is_file():
                        seating_chart.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> <img src="%s">"""
                                            % (seat, uni, name, img_rel_path))
                    else:
                        print(f"WARNING: no img found for {img_path}")
                        seating_chart.write("""<span class="seat">%s</span><br> %s<br> <span class="name">%s</span><br> """
                                            % (seat, uni, name))
                except KeyError:
                    seating_chart.write(
                        """<span class="seat">%s</span>""" % (seat))
                seating_chart.write("</td>\n")

            for _ in range(maxrow - row_count):
                seating_chart.write("<td></td>\n")

            seating_chart.write("</tr>\n\n")
        seating_chart.write("</table></body>")

if __name__ == "__main__":
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

    main(args)
